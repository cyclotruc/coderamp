import reflex as rx
from ..components import instance_table, coderamp_table
from ..coderamp_lib.coderamp import Coderamp


class DashboardState(rx.State):
    def refresh_all(self):
        self.refresh_instances()
        self.refresh_coderamps()


@rx.page(route="/dashboard")
def dashboard() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard", size="lg"),
            rx.spacer(),
            rx.button("Refresh all", on_click=DashboardState.refresh_all),
            width="100%",
            padding="4",
        ),
        instance_table(),
        coderamp_table(),
        width="90%",
        spacing="4",
    )
