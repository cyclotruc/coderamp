import reflex as rx


@rx.page(route="/")
def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Welcome to Coderamp"),
            rx.button("Create a new Coderamp", on_click=rx.redirect("/create")),
            rx.button("Go to dashboard", on_click=rx.redirect("/dashboard")),
        ),
    )
