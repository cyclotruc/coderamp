import reflex as rx
from ..coderamp_lib.coderamp import Coderamp


class MagicState(rx.State):
    found: bool = False
    instance_url: str = None

    @rx.background
    async def find_coderamp(self):
        async with self:
            self.reset()
        id = self.router.page.params["id"]
        session_id = self.router.session.session_id

        ramp = Coderamp.select().where(Coderamp.slug == id).first()
        if ramp:
            instance = await ramp.allocate_session(session_id)
            async with self:
                print(f"Allocated to {session_id}")
                self.found = True
                self.instance_url = instance.public_url
        # TODO handle not ready
        # TODO handle not found


@rx.page(route="/new", on_load=MagicState.find_coderamp)
def new() -> rx.Component:
    id = MagicState.router.page.params["id"]

    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading(
                    f"Redirecting to {id}",
                    size="lg",
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
