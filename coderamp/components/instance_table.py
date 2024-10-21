import reflex as rx
from datetime import timedelta
from ..coderamp_lib.coderamp import Instance
import asyncio
from reflex.utils.prerequisites import get_app


class InstanceTableState(rx.State):
    instances: list[dict] = []
    update: bool = False
    time: int = 0
    is_autorefreshing: bool = False

    def load_entries(self):
        instances = (
            Instance.select()
            .where(Instance.state != "retired")
            .order_by(Instance.created_at.desc())
            .limit(10)
        )
        updated_instances = []
        for instance in instances:
            updated_instances.append(
                {
                    "name": instance.name,
                    "age": instance.created_at + timedelta(hours=2),
                    "link": instance.public_url or "",
                    "accessible": instance.state == "ready"
                    or instance.state == "allocated",
                    "state": instance.state,
                    "ip": instance.public_ip or "",
                    "ports": instance.coderamp.ports or "",
                    "id": instance.get_id(),
                }
            )
        self.time += 1
        self.instances = updated_instances

    async def retire_handler(self, id: int):
        instance = Instance.get_by_id(id)
        await instance.retire()
        self.load_entries()

    async def delete_handler(self, id: int):
        instance = Instance.get_by_id(id)
        if instance.state == "retired":
            await instance.delete()
        else:
            raise ValueError("Instance is not retired")
        self.load_entries()

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

    def stop_autorefresh(self):
        self.is_autorefreshing = False


def instance_row(instance: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(instance["name"]),
        rx.table.cell(rx.moment(instance["age"], from_now=True, interval=1000)),
        rx.table.cell(
            rx.cond(
                (instance["accessible"]),
                rx.link(
                    rx.button("Open"),
                    href=instance["link"].to(str),
                    target="_blank",
                ),
                rx.button("Open", disabled=True),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    instance["state"].to(str) != "retired",
                    rx.button(
                        "Retire",
                        on_click=lambda: InstanceTableState.retire_handler(
                            instance["id"]
                        ),
                        color_scheme="red",
                    ),
                    rx.button("Retire", disabled=True, color_scheme="red"),
                ),
            ),
        ),
        rx.table.cell(
            rx.match(
                instance["state"].to(str),
                (
                    "created",
                    rx.badge(
                        "Created", color_scheme="gold", variant="surface", radius="full"
                    ),
                ),
                (
                    "provisioning",
                    rx.badge(
                        "Provisioning",
                        color_scheme="amber",
                        variant="soft",
                        radius="full",
                    ),
                ),
                (
                    "provisioned",
                    rx.badge(
                        "Provisioned",
                        color_scheme="amber",
                        variant="surface",
                        radius="full",
                    ),
                ),
                (
                    "installing",
                    rx.badge(
                        "Installing",
                        color_scheme="orange",
                        variant="outline",
                        radius="full",
                    ),
                ),
                (
                    "ready",
                    rx.badge(
                        "Ready",
                        color_scheme="grass",
                        variant="soft",
                        high_contrast=True,
                        radius="full",
                    ),
                ),
                (
                    "allocated",
                    rx.badge(
                        "Allocated", color_scheme="blue", variant="solid", radius="full"
                    ),
                ),
                (
                    "retired",
                    rx.badge(
                        "Retired", color_scheme="gray", variant="soft", radius="full"
                    ),
                ),
            )
        ),
        rx.table.cell(instance["ip"]),
        rx.table.cell(rx.badge(instance["ports"])),
        rx.table.cell(
            rx.button(
                rx.icon(tag="trash"),
                on_click=lambda: InstanceTableState.delete_handler(instance["id"]),
                color_scheme="gray",
            ),
        ),
        align_items="center",  # Add this line to center items vertically
    )


def instance_table() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.text(InstanceTableState.time),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Name"),
                            rx.table.column_header_cell("Age"),
                            rx.table.column_header_cell(""),
                            rx.table.column_header_cell(""),
                            rx.table.column_header_cell("State"),
                            rx.table.column_header_cell("ip"),
                            rx.table.column_header_cell("ports"),
                            rx.table.column_header_cell(
                                rx.button(
                                    "Refresh", on_click=InstanceTableState.load_entries
                                )
                            ),
                            # rx.table.column_header_cell(
                            #     rx.button(
                            #         "Auto-refresh",
                            #         on_click=InstanceTableState.autorefresh_handler,
                            #     )
                            # ),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(InstanceTableState.instances, instance_row)
                    ),
                    on_mount=InstanceTableState.start_autorefresh,
                ),
            ),
        )
    )
