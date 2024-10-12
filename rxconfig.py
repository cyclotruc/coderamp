import reflex as rx
from dotenv import load_dotenv
import os

load_dotenv()
SCW_ACCESS_KEY = os.getenv("SCW_ACCESS_KEY")
SCW_SECRET_KEY = os.getenv("SCW_SECRET_KEY")
SCW_DEFAULT_ORGANIZATION_ID = os.getenv("SCW_DEFAULT_ORGANIZATION_ID")
SCW_DEFAULT_PROJECT_ID = os.getenv("SCW_DEFAULT_PROJECT_ID")
SCW_DEFAULT_ZONE = os.getenv("SCW_DEFAULT_ZONE")

PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

CADDY_IP = os.getenv("CADDY_IP")

CODERAMP_DOMAIN = os.getenv("CODERAMP_DOMAIN")
ZERO_SSL_KEY_ID = os.getenv("ZERO_SSL_KEY_ID")
ZERO_SSL_MAC_KEY = os.getenv("ZERO_SSL_MAC_KEY")

config = rx.Config(
    app_name="coderamp",
    api_url=f"https://{CODERAMP_DOMAIN}/reflex",
)
