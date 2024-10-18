import reflex as rx
from datetime import datetime, timedelta
from ..coderamp_lib.coderamp import Coderamp


class CoderampTableState(rx.State):
    coderamps: list[dict] = []
    update: bool = False

    def load_entries(self):
        coderamps = Coderamp.select().order_by(Coderamp.created_at.desc()).limit(10)
        updated_coderamps = []
        for coderamp in coderamps:
            updated_coderamps.append(
                {
                    "id": coderamp.get_id(),
                    "name": coderamp.name,
                    "age": coderamp.created_at + timedelta(hours=2),
                    "active": coderamp.active,
                    "vm_type": coderamp.vm_type,
                    "magic_link": coderamp.magic_url,
                }
            )
        self.coderamps = updated_coderamps

    async def stop_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        await coderamp.stop()
        self.load_entries()

    async def start_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        await coderamp.start()
        self.load_entries()

    async def delete_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        await coderamp.delete_coderamp()
        self.load_entries()


def coderamp_row(coderamp: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(coderamp["name"]),
        rx.table.cell(rx.moment(coderamp["age"], from_now=True, interval=1000)),
        rx.table.cell(
            rx.cond(
                (coderamp["active"]),
                rx.badge(
                    "Active", color_scheme="green", radius="full", variant="solid"
                ),
                rx.badge(
                    "Inactive", color_scheme="red", radius="full", variant="solid"
                ),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    coderamp["active"],
                    rx.button(
                        "Stop",
                        on_click=lambda: CoderampTableState.stop_handler(
                            coderamp["id"]
                        ),
                        color_scheme="gray",
                    ),
                    rx.button(
                        "Start",
                        on_click=lambda: CoderampTableState.start_handler(
                            coderamp["id"]
                        ),
                        color_scheme="green",
                    ),
                ),
            ),
        ),
        rx.table.cell(coderamp["ip"]),
        rx.table.cell(
            rx.link(
                f"{coderamp['magic_link'].to(str)}",
                href=coderamp["magic_link"].to(str),
                target="_blank",
            )
        ),
    )


def coderamp_table() -> rx.Component:
    return rx.center(
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("name"),
                        rx.table.column_header_cell("age"),
                        rx.table.column_header_cell("vm_type"),
                        rx.table.column_header_cell("magic_link"),
                        rx.table.column_header_cell("start_button"),
                        rx.table.column_header_cell("stop_button"),
                        rx.table.column_header_cell(
                            rx.button(
                                "Refresh", on_click=CoderampTableState.load_entries
                            )
                        ),
                    ),
                ),
                rx.table.body(rx.foreach(CoderampTableState.coderamps, coderamp_row)),
                on_mount=CoderampTableState.load_entries,
            )
        )
    )
