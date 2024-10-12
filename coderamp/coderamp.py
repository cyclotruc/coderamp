import asyncio
import reflex as rx
from rxconfig import config
from coderamp.coderamp_lib.coderamp import Coderamp


class State(rx.State):
    pass


async def global_tick():
    try:
        print("Global tick started")
        while True:
            for coderamp in Coderamp.select():
                await coderamp.tick()

            # input()
            await asyncio.sleep(10)

    except asyncio.CancelledError:
        print("Global tick was stopped")


app = rx.App()
app.register_lifespan_task(global_tick)
