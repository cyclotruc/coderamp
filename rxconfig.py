import reflex as rx
from dotenv import load_dotenv
import os

load_dotenv()
CODERAMP_DOMAIN = os.getenv("CODERAMP_DOMAIN")

config = rx.Config(
    app_name="coderamp",
    api_url=f"https://{CODERAMP_DOMAIN}/reflex",
)
