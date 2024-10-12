import reflex as rx
from ..coderamp_lib.coderamp import Instance


class InstanceTableState(rx.State):
    instances: list = []

    def refresh_instances(self):
        self.instances = []
        all_instances = Instance.select()
        for instance in all_instances:
            id = instance.id or "None"
            name = instance.name or "None"
            state = instance.state or "None"
            public_ip = instance.public_ip or "None"
            self.instances.append([id, name, state, public_ip])


def instance_table() -> rx.Component:
    return rx.vstack(
        rx.heading("Instances", size="lg"),
        rx.data_table(
            data=InstanceTableState.instances,
            columns=["id", "name", "state", "public_ip"],
            pagination=True,
            search=True,
            sort=True,
            width="100%",
        ),
        on_mount=InstanceTableState.refresh_instances,
    )
