import asyncio
import reflex as rx

from rxconfig import config

from coderamp.coderamp_lib.coderamp import Instance, Coderamp

# TODO:
# https://reflex.dev/blog/2023-10-25-implementing-sign-in-with-google/
# or https://kroo.github.io/reflex-clerk/


class FormState(rx.State):
    name: str = ""
    git_url: str = ""
    commands: str = ""
    ports: str = ""

    def handle_submit(self, form_data):
        self.name = form_data["name"]
        self.git_url = form_data["url"] if "url" in form_data else None
        self.ports = form_data["ports"] if "ports" in form_data else None
        self.commands = form_data["commands"]
        ramp = Coderamp.create(name=self.name, url=self.git_url, commands=self.commands)
        ramp.configure(
            name=self.name,
            git_url=self.git_url,
            setup_commands=self.commands,
            ports=self.ports,
        )

        print(f"Received: {self.name}, {self.git_url}, {self.commands}")


class State(rx.State):
    """The app state."""

    instances: list = []
    coderamps: list = []

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
            id = coderamp.id or "None"
            name = coderamp.name or "None"
            uuid = str(coderamp.uuid) or "None"
            created_at = str(coderamp.created_at) or "None"
            current_instances = coderamp.current_instances or "None"

            self.coderamps.append([id, name, uuid, created_at, current_instances])


class MagicState(rx.State):
    found: bool = False
    instance_url: str = None

    @rx.background
    async def find_coderamp(self):
        async with self:
            self.reset()
        id = self.router.page.params["id"]
        session_id = self.router.session.session_id

        print(f"Finding instance {id}")
        ramp = Coderamp.select().where(Coderamp.slug == id).first()
        if ramp:
            instance = await ramp.allocate_session(session_id)
            async with self:
                print(f"Found!! and allocated to {session_id}")
                self.found = True
                self.instance_url = instance.public_url
        # TODO handle not ready
        # TODO handle not found


@rx.page(route="/new", on_load=MagicState.find_coderamp)
def new() -> rx.Component:
    id = State.router.page.params["id"]

    instance_url = MagicState.instance_url
    return rx.vstack(
        rx.heading(
            f"Redirecting to {id}",
        ),
        rx.cond(
            MagicState.found,
            rx.fragment(rx.script(f"window.location.href = '{instance_url}'")),
            rx.spinner(size="3"),
        ),
    )


@rx.page(route="/create")
def create() -> rx.Component:
    return rx.center(
        rx.container(
            rx.vstack(
                create_form(),
                coderamps_table(),
                width="100%",
            ),
        ),
    )


def create_form() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Create a new Coderamp"),
                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="Coderamp name",
                            name="name",
                        ),
                        rx.input(
                            placeholder="Github URL",
                            name="git_url",
                        ),
                        rx.text_area(
                            placeholder="Startup commands, separated by newlines",
                            name="commands",
                        ),
                        rx.button("Create", type="submit"),
                    ),
                    on_submit=FormState.handle_submit,
                    reset_on_submit=True,
                ),
            ),
            width="400px",
        )
    )


def dummy_page(username, session_id) -> rx.Component:
    return rx.vstack(
        rx.heading(f"Dummyaaaa page {username['id']} {session_id}"),
        rx.button("Back", on_click=rx.redirect("https://codesandboxbeta.cloud")),
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
        on_mount=State.refresh_instances,
    )


def coderamps_table() -> rx.Component:
    return rx.vstack(
        rx.heading("Coderamps", size="lg"),
        rx.spacer(),
        rx.button("Refresh Coderamps", on_click=State.refresh_coderamps),
        rx.data_table(
            data=State.coderamps,
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
        on_mount=State.refresh_coderamps,
    )


@rx.page(route="/dashboard")
def instances() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard", size="lg"),
            rx.spacer(),
            rx.button("Refresh all", on_click=State.refresh_all),
            width="100%",
            padding="4",
        ),
        instances_table(),
        coderamps_table(),
        width="90%",
        spacing="4",
    )


@rx.page(route="/")
def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Welcome to Coderamp"),
        rx.button("Create a new Coderamp", on_click=rx.redirect("/create")),
    )


async def global_tick():
    try:
        while True:
            await asyncio.sleep(5)
            print("global tick")
    except asyncio.CancelledError:
        # clean up if needed
        print("Task was stopped")


app = rx.App()
app.register_lifespan_task(global_tick)
