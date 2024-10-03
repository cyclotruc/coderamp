import asyncio 
import reflex as rx

from rxconfig import config

from coderamp.coderamp_lib.coderamp import Instance, Coderamp

# TODO:
# https://reflex.dev/blog/2023-10-25-implementing-sign-in-with-google/
# or https://kroo.github.io/reflex-clerk/


class State(rx.State):
    """The app state."""

    instances: list[Instance] = []
    coderamps: list[Coderamp] = []

    @rx.background
    async def create_instance(self):
        for coderamp in Coderamp.select():
            await coderamp.new_instance()


    def refresh_all(self):
        self.refresh_instances()
        self.refresh_coderamps()

    def refresh_instances(self):
        self.instances = []
        all_instances = Instance.select()
        for instance in all_instances:
            print(instance)
            id = instance.id or "None"
            name = instance.name or "None"
            state = instance.state or "None"
            public_ip = instance.public_ip or "None"

            self.instances.append([id, name, state, public_ip])

    def refresh_coderamps(self):
        self.coderamps = []
        all_coderamps = Coderamp.select()
        for coderamp in all_coderamps:
            print(coderamp)
            id = coderamp.id or "None"
            name = coderamp.name or "None"
            base_url = coderamp.base_url or "None"
            uuid = str(coderamp.uuid) or "None"
            created_at = str(coderamp.created_at) or "None"
            max_instances = coderamp.max_instances or "None"
            current_instances = coderamp.current_instances or "None"

            self.coderamps.append(
                [id, name, base_url, uuid, created_at, max_instances, current_instances]
            )


@rx.page(route="/user")
def show_user_page():
        return dummy_page(State.router.page.params, State.router.session.session_id)


def dummy_page(username, session_id) -> rx.Component:
    return rx.vstack(
        rx.heading(f"Dummyaaaa page {username['id']} {session_id}"),
        rx.button("Back", on_click=rx.redirect("https://codesandboxbeta.cloud") ),
    )


def instances_table() -> rx.Component:
    return rx.vstack(
        rx.heading("Instances", size="lg"),
        rx.data_table(
            data=State.instances,
            columns=["id", "name", "state", "public_ip"],
            pagination=True,
            search=True,
            sort=True,
            width="100%",
        ),
    )


def coderamps_table() -> rx.Component:
    return rx.vstack(
        rx.heading("Coderamps", size="lg"),
        rx.data_table(
            data=State.coderamps,
            columns=[
                "id",
                "name",
                "base_url",
                "uuid",
                "created_at",
                "max_instances",
                "current_instances",
            ],
            pagination=True,
            search=True,
            sort=True,
            width="100%",
        ),
        width="100%",
        padding="4",
    )


@rx.page(route="/dashboard")
def instances() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard", size="lg"),
            rx.spacer(),
            rx.button("Refresh", on_click=State.refresh_all),
            rx.button("Create Instance", on_click=State.create_instance),
            width="100%",
            padding="4",
        ),
        instances_table(),
        coderamps_table(),
        width="90%",
        spacing="4",
    )


async def global_tick():
    try:
        while True:
            await asyncio.sleep(
                5
            )
            print("global tick")
    except asyncio.CancelledError:
         # clean up if needed
        print("Task was stopped")


app = rx.App()
app.register_lifespan_task(global_tick)
