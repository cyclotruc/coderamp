import asyncio
import reflex as rx
from rxconfig import config
from coderamp.coderamp_lib.coderamp import Coderamp, full_reset


async def global_tick():
    # full_reset()
    # ramp1 = Coderamp.create()
    # ramp1.configure(
    #     "Basic",
    #     open_file="pages/index.md",
    #     open_folder="/root/evidence-starter",
    #     setup_commands="",
    #     ports="3000",
    #     vm_type="DEV1-S",
    #     min_instances=1,
    # )
    try:
        print("Global tick started")
        while True:
            for coderamp in Coderamp.select().where(Coderamp.active == True):
                await coderamp.tick()

            # input()
            await asyncio.sleep(10)

    except asyncio.CancelledError:
        print("Global tick was stopped")


app = rx.App()
app.register_lifespan_task(global_tick)
