import reflex as rx


class AuthState(rx.State):
    is_authenticated: bool = False
    password: str = ""

    def login(self):
        if self.password == "cerise25":
            self.is_authenticated = True
        else:
            self.is_authenticated = False
            self.password = ""

    def logout(self):
        self.is_authenticated = False
        self.password = ""


def login_form():
    return rx.vstack(
        rx.input(
            placeholder="Enter password",
            type="password",
            on_change=AuthState.set_password,
        ),
        rx.button("Login", on_click=AuthState.login),
    )
