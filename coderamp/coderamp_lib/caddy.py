from .tools import write_to_file
from rxconfig import (
    CODERAMP_DOMAIN,
    MAIN_CADDY_IP,
    CODERAMP_CADDY_IP,
    ZERO_SSL_KEY_ID,
    ZERO_SSL_MAC_KEY,
)


def generate_main_caddyfile():
    caddyfile = ""
    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/main", "r") as file:
        caddyfile = file.read()

    with open(
        "/root/coderamp/coderamp/coderamp_lib/caddy_templates/acme_provider", "r"
    ) as file:
        acme_provider = file.read()

    acme_provider = acme_provider.replace("{key_id}", ZERO_SSL_KEY_ID)
    acme_provider = acme_provider.replace("{mac_key}", ZERO_SSL_MAC_KEY)
    caddyfile = caddyfile.replace("{acme_provider}", acme_provider)

    caddyfile = (
        caddyfile.replace("{domain}", CODERAMP_DOMAIN)
        .replace("{key_id}", ZERO_SSL_KEY_ID)
        .replace("{mac_key}", ZERO_SSL_MAC_KEY)
    )

    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/web") as file:
        web = file.read()
    caddyfile = caddyfile.replace("{web}", web)
    return caddyfile


def generate_coderamp_caddyfile(instances):
    caddyfile = "{acme_provider}\n{coderamps}\n{ports}"

    with open(
        "/root/coderamp/coderamp/coderamp_lib/caddy_templates/acme_provider", "r"
    ) as file:
        acme_provider = file.read()

    acme_provider = acme_provider.replace("{key_id}", ZERO_SSL_KEY_ID)
    acme_provider = acme_provider.replace("{mac_key}", ZERO_SSL_MAC_KEY)
    caddyfile = caddyfile.replace("{acme_provider}", acme_provider)
    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/coderamp") as file:
        coderamp = file.read()

    coderamp_redirects = ""
    for i in instances:
        coderamp_redirects += (
            coderamp.replace("{ip}", f"{i.public_ip}")
            .replace("{uuid}", f"{i.uuid}")
            .replace("{domain}", CODERAMP_DOMAIN)
        )
        coderamp_redirects += "\n"

    caddyfile = caddyfile.replace("{coderamps}", coderamp_redirects)

    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/port") as file:
        ports = file.read()

    ports_redirects = ""
    for i in instances:
        if i.coderamp.ports:
            for port in i.coderamp.ports.split(","):
                ports_redirects += (
                    ports.replace("{port}", port)
                    .replace("{ip}", i.public_ip)
                    .replace("{uuid}", f"{i.uuid}")
                    .replace("{domain}", CODERAMP_DOMAIN)
                )
                ports_redirects += "\n"
    caddyfile = caddyfile.replace("{ports}", ports_redirects)

    with open("Caddyfile", "w") as f:
        f.write(caddyfile)
    return caddyfile


async def update_main_caddyfile():
    caddyfile = generate_main_caddyfile()
    await write_to_file(MAIN_CADDY_IP, caddyfile, "/root/Caddyfile")


async def update_coderamp_caddyfile(instances):
    print("Updating coderamp caddyfile")
    caddyfile = generate_coderamp_caddyfile(instances)
    await write_to_file(CODERAMP_CADDY_IP, caddyfile, "/root/Caddyfile")
