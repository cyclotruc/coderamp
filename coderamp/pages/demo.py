import reflex as rx
from ..coderamp_lib.coderamp import Coderamp


class DemoState(rx.State):
    ready: bool = False
    name: str = ""
    url: str = ""
    ports: str = ""
    active: bool = False
    id: str = ""
    created_at: str = ""
    cpu: str = ""
    memory: str = ""

    def get_config(self):
        print("Getting config//" * 10)
        try:
            ramp = Coderamp.select().where(Coderamp.slug == "evidence_demo").first()
            print(ramp, ramp.name)
            if ramp:
                self.name = ramp.name
                self.url = ramp.magic_url
                self.ports = ramp.ports
                self.cpu = "4"
                self.memory = "8"
                self.id = ramp.uuid
                self.active = ramp.ready
                self.created_at = ramp.created_at
                self.ready = True

        except Exception as e:
            print(e)


def port_badge(port: str) -> rx.Component:
    return rx.badge(port)


@rx.page(route="/demo", on_load=DemoState.get_config)
def demo() -> rx.Component:
    return (
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.image(
                        src="https://raw.githubusercontent.com/evidence-dev/media-kit/refs/heads/main/png/logo-round-black-on-white.png",
                        alt="My Icon",
                        width="50px",
                        height="50px",
                    ),
                    rx.heading("Evidence.dev"),
                ),
                rx.spacer(),
                rx.hstack(
                    rx.card(
                        rx.data_list.root(
                            rx.data_list.item(
                                rx.data_list.label("Name"),
                                rx.data_list.value(DemoState.name),
                            ),
                            rx.data_list.item(
                                rx.data_list.label("Ports"),
                                rx.data_list.value(
                                    rx.foreach(DemoState.ports.split(","), port_badge)
                                ),
                            ),
                            rx.data_list.item(
                                rx.data_list.label("Documentation"),
                                rx.data_list.value(
                                    rx.link(
                                        "Install Evidence",
                                        href="https://docs.evidence.dev/install-evidence/",
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                rx.vstack(
                    rx.text(
                        "This button will open a new vscode instance with the Evidence"
                    ),
                    rx.button(
                        "Open Evidence",
                        on_click=rx.redirect(
                            "https://codesandboxbeta.cloud/new?id=evidence_demo"
                        ),
                    ),
                ),
            ),
        ),
    )
