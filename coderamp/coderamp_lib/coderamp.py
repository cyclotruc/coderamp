import os
import uuid
import asyncio
from dotenv import load_dotenv
from peewee import *
from datetime import datetime, timedelta
from .scaleway import delete_all_codeboxes, provision_instance, terminate_instance
from .install import setup_coderamp
from .caddy import update_caddy

load_dotenv()
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

db = PostgresqlDatabase(
    "coderamp_dev",
    user=PG_USER,
    password=PG_PASSWORD,
    host="localhost",
    port=5432,
)


class Coderamp(Model):

    uuid = UUIDField(unique=True, default=uuid.uuid4)
    created_at = DateTimeField(default=datetime.now)
    total_instances = IntegerField(default=0)
    max_instances = IntegerField(default=10)
    ready = BooleanField(default=False)

    # User-input defined variables, they are set in configure:
    name = TextField(null=True, default=None)
    slug = TextField(null=True, default=None)
    magic_url = TextField(null=True, default=None)
    git_url = TextField(null=True, default=None)
    setup_commands = TextField(null=True, default=None)
    ports = TextField(null=True, default=None)
    timeout = IntegerField(default=3600)
    vm_type = CharField(default="DEV1-S")
    open_file = TextField(null=True, default=None)
    open_folder = TextField(null=True, default=None)
    min_instances = IntegerField(default=1)
    # workspace_folder_name = TextField(null=True, default=None)

    class Meta:
        database = db
        table_name = "coderamp"

    def configure(
        self,
        name,
        open_file="",
        open_folder="/",
        git_url="",
        setup_commands="",
        ports="",
        vm_type="DEV1-S",
        timeout=3600,
        min_instances=1,
    ):
        self.name = name
        self.open_file = open_file
        self.open_folder = open_folder
        self.slug = name.lower().replace(" ", "-")
        self.magic_url = f"https://codesandboxdemo.cloud/new/?id={self.slug}"
        self.git_url = git_url
        self.vm_type = vm_type
        self.timeout = timeout
        self.setup_commands = setup_commands
        self.ports = ports
        self.ready = True
        self.min_instances = min_instances
        self.save()

    async def new_instance(self):
        if self.ready:
            instance = Instance.create(name=self.name, state="created", coderamp=self)
            await instance.provision()
            await instance.setup()
            await update_caddy(
                Instance.select().where(
                    (Instance.state == "ready") | (Instance.state == "allocated")
                )
            )
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

    async def tick(self):
        print(f"[CODERAMP TICK - {self.slug}]")
        ready_instances = (
            Instance.select()
            .where((Instance.coderamp == self.get_id()) & (Instance.state == "ready"))
            .count()
        )

        provisioning_instances = (
            Instance.select()
            .where(
                (Instance.coderamp == self.get_id())
                & (Instance.state.in_(["created", "provisioned"]))
            )
            .count()
        )

        total_provisioning_instances = ready_instances + provisioning_instances
        print(f"|Provisioning instances: {total_provisioning_instances}")

        if total_provisioning_instances < self.min_instances:
            for _ in range(self.min_instances - total_provisioning_instances):
                print(f"+ Provisioning new instance to reach {self.min_instances}")
                asyncio.create_task(self.new_instance())
                await asyncio.sleep(0)

        # Delete instances that are too old to survive
        old_instances = Instance.select().where(
            (Instance.coderamp == self.get_id())
            & (Instance.state != "terminated")
            & (Instance.created_at < datetime.now() - timedelta(seconds=self.timeout))
        )

        for instance in old_instances:
            print(f"- Terminating old instance: {instance.uuid}")
            asyncio.create_task(instance.terminate())
            await asyncio.sleep(0)

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
            raise Exception("No instance available to allocate")


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

    async def provision(self):
        id, ip = await provision_instance(
            f"{self.coderamp.slug}-{self.uuid}", self.coderamp.vm_type
        )
        self.remote_id = id
        self.public_ip = ip
        self.state = "provisioned"
        self.save()

    async def setup(self):
        await setup_coderamp(self)
        self.state = "ready"
        self.public_url = f"https://{self.uuid}.codesandboxbeta.cloud/?folder={self.coderamp.open_folder}"
        self.save()

    def allocate(self, session_id):
        self.allocated_to_session_id = session_id
        self.allocated_at = datetime.now()
        self.state = "allocated"
        self.save()

    async def terminate(self):
        terminate_instance(self.remote_id)
        self.public_ip = None
        self.allocated_to_session_id = None
        self.state = "terminated"
        self.save()

    class Meta:
        database = db
        table_name = "instances"


def full_reset():
    reset_instances()
    reset_coderamps()


def reset_instances():
    db.drop_tables([Instance])
    db.create_tables([Instance])
    delete_all_codeboxes()


def reset_coderamps():
    db.drop_tables([Coderamp])
    db.create_tables([Coderamp])
