import reflex as rx
from ..coderamp_lib.coderamp import Coderamp


class CoderampTableState(rx.State):

    coderamps: list = []

    def refresh_coderamps(self):
        self.coderamps = []
        all_coderamps = Coderamp.select()
        for coderamp in all_coderamps:
            id = coderamp.id or "None"
            name = coderamp.name or "None"
            uuid = str(coderamp.uuid) or "None"
            created_at = str(coderamp.created_at) or "None"
            self.coderamps.append([id, name, uuid, created_at])


def coderamp_table() -> rx.Component:
    return rx.vstack(
        rx.heading("Coderamps", size="lg"),
        rx.spacer(),
        rx.button("Refresh Coderamps", on_click=CoderampTableState.refresh_coderamps),
        rx.data_table(
            data=CoderampTableState.coderamps,
            columns=[
                "id",
                "name",
                "uuid",
                "created_at",
            ],
            pagination=True,
            search=True,
            sort=True,
            width="100%",
        ),
        width="100%",
        on_mount=CoderampTableState.refresh_coderamps,
    )
