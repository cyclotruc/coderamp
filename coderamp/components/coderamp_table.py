import asyncio

import reflex as rx
from reflex.utils.prerequisites import get_app
from datetime import datetime, timedelta
from ..coderamp_lib.coderamp import Coderamp


class CoderampTableState(rx.State):
    coderamps: list[dict] = []
    update: bool = False
    time: int = 0
    is_autorefreshing: bool = False
    ascii_loader: str = ""

    def get_ascii_loader(self, time: int):
        loader = ["𓃉𓃉𓃉", "𓃉𓃉∘", "𓃉∘°", "∘°∘", "°∘𓃉", "∘𓃉𓃉"]
        return loader[time % len(loader)]

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
                    "magic_link": coderamp.magic_url or "",
                    "ports": coderamp.ports or "",
                    "min_instances": coderamp.min_instances or "",
                }
            )
        self.time += 1
        self.ascii_loader = self.get_ascii_loader(self.time)
        self.coderamps = updated_coderamps

    @rx.background
    async def start_autorefresh(self):
        async with self:
            self.is_autorefreshing = True
        app_object = get_app()
        while self.is_autorefreshing:
            async with self:
                self.load_entries()
            yield
            await asyncio.sleep(1)
            client_still_connected = (
                self.router.session.client_token
                in app_object.app.event_namespace.token_to_sid
            )
            if not client_still_connected:
                async with self:
                    self.is_autorefreshing = False

    async def increment_min_instances_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        if coderamp:
            coderamp.increment_min_instances()
        else:
            raise Exception("Coderamp not found")

    async def decrement_min_instances_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        if coderamp:
            coderamp.decrement_min_instances()
        else:
            raise Exception("Coderamp not found")

    async def stop_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        if coderamp:
            coderamp.stop()
        else:
            raise Exception("Coderamp not found")

    async def start_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        if coderamp:
            coderamp.start()
        else:
            raise Exception("Coderamp not found")

    async def delete_handler(self, id: int):
        coderamp = Coderamp.get_by_id(id)
        if coderamp:
            print(f"Deleting coderamp: {coderamp.uuid}")
            print(f"Coderamp dir {dir(coderamp)}")
            await coderamp.delete_from_db()
        else:
            raise Exception("Coderamp not found")


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
            rx.cond(
                coderamp["active"],
                rx.button(
                    "Stop",
                    on_click=lambda: CoderampTableState.stop_handler(coderamp["id"]),
                    color_scheme="gray",
                ),
                rx.button(
                    "Start",
                    on_click=lambda: CoderampTableState.start_handler(coderamp["id"]),
                    color_scheme="green",
                ),
            ),
        ),
        rx.table.cell(
            rx.link(
                f"{coderamp['magic_link'].to(str)}",
                href=coderamp["magic_link"].to(str),
                target="_blank",
            )
        ),
        rx.table.cell(rx.badge(coderamp["ports"])),
        rx.table.cell(
            rx.button(
                "Delete",
                on_click=lambda: CoderampTableState.delete_handler(coderamp["id"]),
                color_scheme="red",
            ),
        ),
        rx.table.cell(
            rx.badge(coderamp["min_instances"]),
        ),
        rx.table.cell(
            rx.vstack(
                rx.button(
                    "+",
                    on_click=lambda: CoderampTableState.increment_min_instances_handler(
                        coderamp["id"]
                    ),
                    color_scheme="green",
                ),

                rx.button(
                    "-",
                    on_click=lambda: CoderampTableState.decrement_min_instances_handler(
                        coderamp["id"]
                    ),
                    color_scheme="red",
                ),
            ),
        ),
    )


def coderamp_table() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.text(CoderampTableState.ascii_loader),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Name"),
                            rx.table.column_header_cell("Age"),
                            rx.table.column_header_cell("State"),
                            rx.table.column_header_cell(""),
                            rx.table.column_header_cell("Magic Link"),
                            rx.table.column_header_cell("Ports"),
                            rx.table.column_header_cell("Info"),
                            rx.table.column_header_cell("Max Instances"),
                            rx.table.column_header_cell(""),
                            rx.table.column_header_cell(
                                rx.button(
                                    "Refresh", on_click=CoderampTableState.load_entries
                                )
                            ),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(CoderampTableState.coderamps, coderamp_row)
                    ),
                    on_mount=CoderampTableState.start_autorefresh,
                ),
            ),
        ),
    )
