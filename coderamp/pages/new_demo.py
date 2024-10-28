import reflex as rx

from ..coderamp_lib.coderamp import Coderamp
from rxconfig import CODERAMP_DOMAIN

from reflex_monaco import monaco




class DemoState(rx.State):
    pass



@rx.page(route="/new_demo")
def new_demo():
    return rx.container(
        monaco(
            default_language="markdown",
            default_value='''---
''',
            height='500px',
            width='100%'
        )
    )