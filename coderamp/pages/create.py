import reflex as rx
from ..components import create_form


@rx.page(route="/create")
def create() -> rx.Component:
    return rx.center(
        rx.container(
            rx.vstack(
                create_form(),
                width="100%",
            ),
        ),
    )
