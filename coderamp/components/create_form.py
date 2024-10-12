import reflex as rx
from ..coderamp_lib.coderamp import Coderamp


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
