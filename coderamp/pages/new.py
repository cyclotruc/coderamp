import asyncio

import reflex as rx
from ..coderamp_lib.coderamp import Coderamp


class MagicState(rx.State):
    found: bool = False
    instance_url: str = None

    need_to_wait: bool = False
    display_message: str = ""

    @rx.background
    async def find_coderamp(self):
        id = self.router.page.params["id"]
        token = self.router.session.client_token
        session_id = self.router.session.session_id

        ramp = Coderamp.select().where(Coderamp.slug == id).first()

        if not ramp:
            raise Exception("Invalid Coderamp id")

        instance = await ramp.allocate_session(session_id)

        async with self:
            self.display_message = "Waiting for instance to be ready"
        yield

        while not instance:
            async with self:
                self.need_to_wait = True
                self.display_message = self.display_message + "."
            yield
            print(f"{session_id} Waiting for instance to be ready -> {token}")

            await asyncio.sleep(3)
            instance = await ramp.allocate_session(session_id)

        async with self:
            self.instance_url = instance.public_url
            self.need_to_wait = False
            self.found = True
        yield

        print(f"{session_id} FOUND INSTANCE")


@rx.page(route="/new", on_load=MagicState.find_coderamp)
def new() -> rx.Component:
    id = MagicState.router.page.params["id"]

    return rx.center(
        rx.card(
            rx.vstack(
                rx.cond(
                    MagicState.need_to_wait,
                    rx.vstack(
                        rx.heading(f"Uh oh...", size="lg"),
                        rx.heading(
                            f"Looks like too many people are using this coderamp",
                            size="md",
                        ),
                        rx.text("You will be redirected once we're ready"),
                        rx.text(MagicState.display_message),
                    ),
                    rx.heading(
                        f"Redirecting to {id}",
                        size="lg",
                    ),
                ),
                rx.cond(
                    MagicState.found,
                    rx.fragment(
                        rx.script(f"window.location.href = '{MagicState.instance_url}'")
                    ),
                    rx.spinner(size="xl", color="blue.500"),
                ),
                spacing="4",
                align="center",
            ),
            width="auto",
            padding="6",
            border_radius="lg",
            box_shadow="lg",
        ),
        height="100vh",
    )


# class State(rx.State):
#     display_message: str = ""

#     @rx.background
#     async def background_update(self):
#         while True:
#             async with self:

#                 self.display_message += "."
#                 print(f"{self.router.session.session_id} Updating")
#             yield

#             await asyncio.sleep(1)


# @rx.page(route="/new", on_load=State.background_update)
# def new() -> rx.Component:
#     return (rx.text(State.display_message),)
