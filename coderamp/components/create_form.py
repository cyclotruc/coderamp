import reflex as rx
from ..coderamp_lib.coderamp import Coderamp


class FormState(rx.State):

    def handle_submit(self, form_data: dict):
        self.form_data = form_data

        # sanitize form_data
        # Clean empty strings to None
        for key, value in form_data.items():
            if value == "":
                form_data[key] = None

        # Build kwargs with non-None values
        kwargs = {"name": form_data["name"]}  # name is required

        all_fields = Coderamp.list_all_fields()

        for field in all_fields:
            if form_data.get(field) is not None:
                kwargs[field] = form_data[field]

        # Handle numeric fields
        if form_data.get("timeout") is not None:
            kwargs["timeout"] = int(form_data["timeout"])

        if form_data.get("min_instances") is not None:
            kwargs["min_instances"] = int(form_data["min_instances"])

        ramp = Coderamp.create(**kwargs)

        ramp.set_ready()
        print(f"Coderamp created and configured with: {kwargs}")


def create_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Create")),
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.input(placeholder="Coderamp name", name="name"),
                    rx.input(placeholder="Git URL", name="git_url"),
                    rx.text_area(
                        placeholder="Setup commands",
                        name="setup_commands",
                        width="100%",
                        height="300px",
                    ),
                    rx.input(placeholder="Ports (comma-separated)", name="ports"),
                    rx.input(placeholder="Open file", name="open_file"),
                    rx.input(placeholder="Open folder", name="workspace_folder"),
                    rx.input(placeholder="Open commands", name="open_commands"),
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
                    rx.input(
                        placeholder="Extensions (comma-separated)",
                        name="extensions",
                    ),
                    rx.button("Submit", type="submit"),
                    rx.dialog.close(rx.button("Close")),
                    width="500px",
                ),
                on_submit=FormState.handle_submit,
                width="100%",
            ),
        ),
    )
