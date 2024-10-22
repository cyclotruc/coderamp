import asyncio


import reflex as rx

from ..components import (
    instance_table,
    coderamp_table,
    create_form,
    login_form,
    AuthState,
)


@rx.page(route="/dashboard")
def dashboard() -> rx.Component:
    return rx.vstack(
        rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                rx.heading("Dashboard", size="lg"),
                rx.spacer(),
                instance_table(),
                coderamp_table(),
                create_form(),
            ),
            login_form(),
        ),
    )
