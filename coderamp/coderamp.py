import asyncio
import reflex as rx
from rxconfig import config

from coderamp.coderamp_lib.coderamp import Coderamp, full_reset


async def global_tick():
    # full_reset()
    try:
        print("Global tick started")
        while True:
            for coderamp in Coderamp.select().where(Coderamp.active == True):
                await coderamp.tick()

            await asyncio.sleep(10)

    except asyncio.CancelledError:
        print("Global tick was stopped")


app = rx.App()
app.register_lifespan_task(global_tick)
