import reflex as rx
import sys

sys.path.append("/root/api/coderamp_api/")
from coderamp_lib.coderamp import Coderamp


class CoderampInfoState(rx.State):
    coderamp: dict = None

    def load_info(self):

        coderamp = (
            Coderamp.select()
            .where(Coderamp.slug == self.router.page.params["id"])
            .first()
        )

        if coderamp:
            self.coderamp = coderamp.to_json()
        else:
            raise Exception("Invalid Coderamp id")

        commands_list = self.coderamp["setup_commands"].split("\n")
        self.coderamp["setup_commands"] = "\n".join(commands_list)
        print(self.coderamp)


@rx.page(route="/info", on_load=CoderampInfoState.load_info)
def info():
    return rx.card(
        rx.vstack(
            rx.text(f"Name: {CoderampInfoState.coderamp['name']}"),
            rx.text(f"Git URL: {CoderampInfoState.coderamp['git_url']}"),
            rx.text(f"Open file: {CoderampInfoState.coderamp['open_file']}"),
            rx.text(f"Open folder: {CoderampInfoState.coderamp['workspace_folder']}"),
            rx.text(f"Extensions: {CoderampInfoState.coderamp['extensions']}"),
            rx.text("Setup commands:"),
            rx.text(
                CoderampInfoState.coderamp["setup_commands"], white_space="pre-wrap"
            ),
            rx.text(f"Ports: {CoderampInfoState.coderamp['ports']}"),
            rx.text(f"VM type: {CoderampInfoState.coderamp['vm_type']}"),
            rx.text(f"Timeout: {CoderampInfoState.coderamp['timeout']}"),
            rx.text(f"Min instances: {CoderampInfoState.coderamp['min_instances']}"),
        )
    )
