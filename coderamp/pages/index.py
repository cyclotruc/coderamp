import reflex as rx


@rx.page(route="/")
def index() -> rx.Component:
    return rx.redirect("https://coderamp.io")
