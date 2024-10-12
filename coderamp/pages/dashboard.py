import reflex as rx
from ..components import (
    instance_table,
    coderamp_table,
)


class DashboardState(rx.State):
    pass


@rx.page(route="/dashboard")
def dashboard() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard", size="lg"),
            rx.spacer(),
            width="100%",
            padding="4",
        ),
        instance_table(),
        coderamp_table(),
        width="100%",
        spacing="4",
    )
