import uuid
import asyncio
import re
import requests

from peewee import *
from datetime import datetime, timedelta
from .scaleway import (
    delete_all_codeboxes,
    provision_instance,
    terminate_instance,
)
from .install import setup_coderamp
from .caddy import update_coderamp_caddyfile
from rxconfig import PG_USER, PG_PASSWORD, CODERAMP_DOMAIN

db = PostgresqlDatabase(
    "coderamp_dev",
    user=PG_USER,
    password=PG_PASSWORD,
    host="localhost",
    port=5432,
)


class Coderamp(Model):
    # Automatically set
    uuid = UUIDField(unique=True, default=uuid.uuid4)
    created_at = DateTimeField(default=datetime.now)
    total_instances = IntegerField(default=0)
    max_instances = IntegerField(default=10)
    ready = BooleanField(default=False)
    active = BooleanField(default=False)
    slug = TextField(null=True, default=None)
    magic_url = TextField(null=True, default=None)

    # User defined

    # mandatory
    name = TextField(default="_default_name")
    vm_type = CharField(default="DEV1-S")
    workspace_folder = TextField(default="/code/ramp")

    # optional
    git_url = TextField(null=True, default=None)
    setup_commands = TextField(null=True, default=None)
    ports = TextField(null=True, default=None)
    extensions = TextField(null=True, default=None)
    timeout = IntegerField(default=3600)
    min_instances = IntegerField(default=1)
    open_file = TextField(null=True, default=None)
    open_commands = TextField(null=True, default=None)

    def set_ready(self):
        self.ready = True
        self.slug = Coderamp.generate_slug(str(self.name))
        self.magic_url = f"https://{CODERAMP_DOMAIN}/new/?id={str(self.slug)}"
        self.save()

    @classmethod
    def list_all_fields(cls):
        fields = {}
        for field in cls._meta.fields.values():
            fields[field.name] = type(field).__name__
        return fields

    class Meta:
        database = db
        table_name = "coderamps"

    def to_json(self):
        return {
            field.name: getattr(self, field.name)
            for field in self._meta.fields.values()
        }

    async def delete_from_db(self):
        print(f"Deleting coderamp: {self.uuid} from database")
        self.delete_instance()

    def start(self):
        print(f"Starting coderamp: {self.slug}")
        self.active = True
        self.save()

    def stop(self):
        print(f"Stopping coderamp: {self.slug}")
        self.active = False
        self.save()

    def increment_min_instances(self):
        self.min_instances += 1
        self.save()

    def decrement_min_instances(self):
        self.min_instances -= 1
        self.save()

    async def new_instance(self):
        if self.ready:
            instance = Instance.create(name=self.name, state="created", coderamp=self)
            await instance.provision()
            await instance.setup()
            self.total_instances += 1
            self.save()
            return instance
        else:
            raise Exception("Failed to provision Instance: Coderamp not ready")

    async def allocate_session(self, session_id):
        instance = (
            Instance.select()
            .where(Instance.coderamp == self.get_id())
            .where(Instance.state == "ready")
            .order_by(Instance.created_at.asc())
            .first()
        )
        if instance:
            instance.allocate(session_id)
            return instance
        else:
            raise Exception("No instance available to allocate")

    async def prune_instances(self):
        timeout_allocated_instances = Instance.select().where(
            (Instance.coderamp == self.get_id())
            & (Instance.state == "allocated")
            & (Instance.allocated_at < datetime.now() - timedelta(seconds=self.timeout))
        )

        long_provisioning_instances = Instance.select().where(
            (Instance.coderamp == self.get_id())
            & (Instance.state.in_(["created", "provisioning"]))
            & (Instance.created_at < datetime.now() - timedelta(seconds=600))
        )

        for instance in timeout_allocated_instances + long_provisioning_instances:
            print(f"| - Terminating old instance: {instance.uuid}")
            asyncio.create_task(instance.retire())
            await asyncio.sleep(0)

    async def reach_min_instances(self):
        res = Instance.select().where(
            (Instance.coderamp == self.get_id())
            & (
                (Instance.state == "created")
                | (Instance.state == "provisioning")
                | (Instance.state == "provisioned")
                | (Instance.state == "installing")
                | (Instance.state == "ready")
            )
        )

        instances_getting_up = len(res)
        # print(f"| Instances getting up: {instances_getting_up}")

        if instances_getting_up < self.min_instances:
            for _ in range(self.min_instances - instances_getting_up):
                print(f"| + Provisioning new instance to reach {self.min_instances}")
                asyncio.create_task(self.new_instance())
                await asyncio.sleep(0)

    async def tick(self):
        # print("______________________________")
        # print(f"|CODERAMP TICK - {self.slug}")
        await self.prune_instances()
        await self.reach_min_instances()
        # print("|_____________________________\n")

    class Meta:
        database = db
        table_name = "coderamp"

    async def allocate_session(self, session_id):
        instance = (
            Instance.select()
            .where(Instance.coderamp == self.get_id())
            .where(Instance.state == "ready")
            .order_by(Instance.created_at.asc())
            .first()
        )
        if instance:
            instance.allocate(session_id)
            return instance
        else:
            return None

    @classmethod
    def generate_slug(cls, name: str):
        # Convert to lowercase and replace spaces with hyphens
        slug = name.lower().replace(" ", "-")
        # Remove any characters that are not alphanumeric, hyphen, or underscore
        slug = re.sub(r"[^a-z0-9-_]", "", slug)
        # Replace multiple consecutive hyphens with a single hyphen
        slug = re.sub(r"-+", "-", slug)
        # Remove leading and trailing hyphens
        slug = slug.strip("-")

        suffix = 0
        while cls.select().where(cls.slug == slug).first():
            suffix += 1
            slug = f"{slug}-{suffix}"

        return slug


instance_states = [
    "created",
    "provisioning",
    "provisioned",
    "installing",
    ###########@
    "ready",
    "allocated",
    ############
    "retired",
]


class Instance(Model):
    uuid = UUIDField(unique=True, default=uuid.uuid4)
    name = CharField()
    state = CharField(default="created")
    created_at = DateTimeField(default=datetime.now)
    remote_id = CharField(null=True, default=None)
    public_ip = CharField(null=True, default=None)
    public_url = CharField(null=True, default=None)
    coderamp = ForeignKeyField(Coderamp, backref="instances")
    allocated_to_session_id = CharField(null=True, default=None)
    allocated_at = DateTimeField(null=True, default=None)
    last_healthcheck_at = DateTimeField(null=True, default=None)

    async def provision(self):
        self.state = "provisioning"
        self.save()
        id, ip = await provision_instance(
            f"{self.coderamp.slug}-{self.uuid}", self.coderamp.vm_type, str(self.uuid)
        )
        self.remote_id = id
        self.public_ip = ip
        self.state = "provisioned"
        self.save()

    async def wait_for_reverse_proxy(self, url):
        ready = False
        while not ready:
            try:
                requests.get(url)
                ready = True
            except requests.exceptions.SSLError:
                # print(f"Waiting for {url} to be ready")
                await asyncio.sleep(1)

    async def setup(self):
        self.state = "installing"
        self.save()
        await update_coderamp_caddyfile(
            Instance.select().where(
                (Instance.state != "retired") & (Instance.public_ip != None)
            )
        )
        self.public_url = f"https://{self.uuid}.{CODERAMP_DOMAIN}/?folder={self.coderamp.workspace_folder}"
        await setup_coderamp(self)

        await self.wait_for_reverse_proxy(self.public_url)
        self.state = "ready"
        self.save()

    def allocate(self, session_id):
        self.allocated_to_session_id = session_id
        self.allocated_at = datetime.now()
        self.state = "allocated"
        self.save()

    async def retire(self):
        if terminate_instance(self.remote_id):
            self.remote_id = None
            self.public_ip = None
        else:
            print(f"Failed to retire instance: {self.uuid}")
        self.allocated_to_session_id = None
        self.state = "retired"
        self.save()

    async def delete_from_db(self):
        print(f"Deleting instance: {self.uuid} from database")
        self.delete_instance()

    class Meta:
        database = db
        table_name = "instances"


def full_reset():
    db.drop_tables([Instance, Coderamp])
    db.create_tables([Instance, Coderamp])
    delete_all_codeboxes()


def reset_instances():
    db.drop_tables([Instance])
    db.create_tables([Instance])
    delete_all_codeboxes()


def reset_coderamps():
    db.drop_tables([Coderamp])
    db.create_tables([Coderamp])
