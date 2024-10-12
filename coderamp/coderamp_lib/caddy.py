from .tools import write_to_file
from rxconfig import CODERAMP_DOMAIN, CADDY_IP, ZERO_SSL_KEY_ID, ZERO_SSL_MAC_KEY


def generate_caddyfile(instances):
    with open(
        "/root/coderamp/coderamp/coderamp_lib/caddy_templates/caddyfile", "r"
    ) as file:
        caddyfile = file.read()

    caddyfile = (
        caddyfile.replace("{domain}", CODERAMP_DOMAIN)
        .replace("{key_id}", ZERO_SSL_KEY_ID)
        .replace("{mac_key}", ZERO_SSL_MAC_KEY)
    )

    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/web") as file:
        web = file.read()
    caddyfile = caddyfile.replace("{web}", web)

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

    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/ports") as file:
        ports = file.read()

    ports_redirects = ""
    for i in instances:
        if i.coderamp.ports:
            for port in i.coderamp.ports.split(","):
                ports_redirects += (
                    ports.replace("{port}", port)
                    .replace("{ip}", i.public_ip)
                    .replace("{uuid}", f"{i.uuid}")
                )
                ports_redirects += "\n"
    caddyfile = caddyfile.replace("{ports}", ports_redirects)

    with open("Caddyfile", "w") as f:
        f.write(caddyfile)
    return caddyfile


async def update_caddy(instances):
    caddyfile = generate_caddyfile(instances)
    await write_to_file(CADDY_IP, caddyfile, "/root/Caddyfile")
