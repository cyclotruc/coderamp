import reflex as rx


@rx.page(route="/")
def index() -> rx.Component:
    return rx.script(
        """
    window.location = "https://coderamp.io"
    """
    )
