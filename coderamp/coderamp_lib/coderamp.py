import os
import uuid
import asyncio
from dotenv import load_dotenv
from peewee import *
from datetime import datetime
from .scaleway import delete_all_codeboxes, provision_instance, terminate_instance
from .install import setup_coderamp

load_dotenv()
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

db = PostgresqlDatabase(
    'coderamp_dev',
    user=PG_USER,
    password=PG_PASSWORD,
    host='localhost',
    port=5432,
    
)


class Coderamp(Model):

    uuid = UUIDField(unique=True, default=uuid.uuid4)
    created_at = DateTimeField(default=datetime.now)
    total_instances = IntegerField(default=0)
    min_instances = IntegerField(default=1)
    max_instances = IntegerField(default=10)
    current_instances = IntegerField(default=0)
    ready = BooleanField(default=False)

    #User-input defined variables, they are set in configure:
    name = TextField(null=True, default=None)
    magic_url = TextField(null=True, default=None)
    code_repo = TextField(null=True, default=None)
    setup_commands = TextField(null=True, default=None)


    class Meta:
        database = db
        table_name = 'coderamp'

    def configure(self, name, code_repo, setup_commands):
        self.name = name
        self.magic_url = f"https://codesandboxdemo.cloud/new/?id={name}"
        self.code_repo = code_repo
        self.setup_commands = setup_commands
        self.ready = True
        self.save()

    async def new_instance(self):
        if self.ready:
            instance = Instance.create(name=self.name, state="created", coderamp=self)
            await instance.provision()
            await instance.setup(self)
            return instance
        else:
            raise Exception("Failed to provision Instance: Coderamp not ready")
        
    async def allocate_session(self, session_id):
        instance = Instance.select().where(Instance.allocated_to_session_id == None).order_by(Instance.created_at.asc()).first()
        if instance:
            instance.allocate(session_id)
            return instance
        else:
            raise Exception("No instance available to allocate")



    # async def tick(self):
    #     print("[TICK]")

    # count ready instances
    #     ready_instances = len(Instance.select().where(Instance.state == "ready"))

    # count provisionning instances
    # if ready + provisionning  < min: 
        # provision new instance

    # fetch all instances too old to survive:
            # delete them





class Instance(Model):
    uuid = UUIDField(unique=True, default=uuid.uuid4)
    name = CharField()
    state = CharField(default="created")
    created_at = DateTimeField(default=datetime.now)
    remote_id = CharField(null=True,default=None)
    public_ip = CharField(null=True,default=None)
    coderamp = ForeignKeyField(Coderamp, backref='instances')
    allocated_to_session_id = CharField(null=True,default=None)


    async def provision(self):
        id, ip = await provision_instance(self.name)
        self.remote_id = id
        self.public_ip = ip
        self.state = "provisioned"
        self.save()

    async def setup(self, coderamp):
        await setup_coderamp(self, coderamp)
        self.state = "ready"
        self.save()

    def allocate(self, session_id):
        self.allocated_to_session_id = session_id
        self.state = "allocated"
        self.save()

    async def terminate(self):
        terminate_instance(self.remote_id)
        self.state = "terminated"
        self.public_ip = None
        self.allocated_to_session_id = None
        self.save()

    class Meta:
        database = db
        table_name = 'instances'

def full_reset():
    reset_db()
    delete_all_codeboxes()

def reset_db():
    db.drop_tables([Coderamp,Instance])
    db.create_tables([Coderamp,Instance])