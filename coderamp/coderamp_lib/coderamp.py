import os
import uuid
import asyncio
from dotenv import load_dotenv
from peewee import *
from datetime import datetime
from .scaleway import delete_all_codeboxes, provision_instance
from .install import setup_coderamp
from .caddy import add_redirect

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
    new_uuid = uuid.uuid4()
    name_string = f'coderamp-test-{new_uuid}'
    name = TextField(default=name_string)
    base_url = TextField(default="https://codesandboxbeta.cloud")
    uuid = UUIDField(unique=True, default=new_uuid)
    created_at = DateTimeField(default=datetime.now)
    max_instances = IntegerField(default=10)
    current_instances = IntegerField(default=0)

    
    class Meta:
        database = db 

    async def new_instance(self):
        print("[NEW_INSTANCE]")
        instance = Instance.create(name=self.name, state="created", coderamp=self)
        await instance.provision()
        await instance.start()
        return instance


class Instance(Model):
    name = CharField()
    state = CharField()
    created_at = DateTimeField(default=datetime.now)
    public_ip = CharField(null=True,default=None)
    coderamp = ForeignKeyField(Coderamp, backref='instances')
    session_id = CharField(null=True,default=None)
    

    async def provision(self):
        ip = await provision_instance(self.name)
        self.public_ip = ip
        self.state = "provisioned"
        self.save()
        print(f"{self.name} provisioned")

    async def start(self):
        await setup_coderamp(self.public_ip)
        self.state = "ready"
        self.save()
        print(f"{self.name} ready")


    class Meta:
        database = db
        table_name = 'instances'

def full_reset():
    reset_db()
    delete_all_codeboxes()

def reset_db():
    db.drop_tables([Coderamp,Instance])
    db.create_tables([Coderamp,Instance])