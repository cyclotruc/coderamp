import reflex as rx
from ..coderamp_lib.coderamp import Coderamp


class FormState(rx.State):
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        self.form_data = form_data

        print(form_data)
        ramp = Coderamp.create(
            name=form_data.get("name"),
            url=form_data.get("git_url"),
            commands=form_data.get("setup_commands"),
        )
        ramp.configure(
            name=form_data.get("name"),
            git_url=form_data.get("git_url", ""),
            setup_commands=form_data.get("setup_commands", ""),
            ports=form_data.get("ports", ""),
            open_file=form_data.get("open_file", "empty"),
            open_folder=form_data.get("open_folder", "Coderamp"),
            timeout=int(form_data.get("timeout", 3600)),
            vm_type=form_data.get("vm_type", "DEV1-S"),
            min_instances=int(form_data.get("min_instances", 1)),
        )
        print(f"Coderamp created and configured: {form_data}")


def create_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Create")),
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.input(placeholder="Coderamp name", name="name"),
                    rx.input(placeholder="Git URL", name="git_url"),
                    rx.text_area(placeholder="Setup commands", name="setup_commands"),
                    rx.input(placeholder="Ports (comma-separated)", name="ports"),
                    rx.input(placeholder="Open file", name="open_file"),
                    rx.input(placeholder="Open folder", name="open_folder"),
                    rx.input(
                        placeholder="Timeout (seconds)",
                        default_value="3600",
                        name="timeout",
                    ),
                    rx.select(
                        ["DEV1-S", "DEV1-M", "DEV1-L"],
                        placeholder="VM Type",
                        name="vm_type",
                        default_value="DEV1-S",
                    ),
                    rx.input(
                        placeholder="Min instances",
                        default_value="1",
                        name="min_instances",
                    ),
                    rx.button("Submit", type="submit"),
                    rx.dialog.close(rx.button("Close")),
                ),
                on_submit=FormState.handle_submit,
            ),
        ),
    )
