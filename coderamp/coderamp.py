import asyncio
import reflex as rx
from rxconfig import config
from coderamp.coderamp_lib.coderamp import Coderamp


class State(rx.State):
    pass


async def global_tick():
    try:
        while True:
            print("[GLOBAL TICK]")
            for coderamp in Coderamp.select():
                await coderamp.tick()
            await asyncio.sleep(5)

    except asyncio.CancelledError:
        print("Global tick was stopped")


app = rx.App()
app.register_lifespan_task(global_tick)
