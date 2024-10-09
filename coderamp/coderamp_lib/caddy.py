import os
from dotenv import load_dotenv
import asyncssh

load_dotenv()
CADDY_PUBLIC_IP = os.getenv("CADDY_PUBLIC_IP")
CADDY_USERNAME = os.getenv("CADDY_USERNAME")


async def remote_ssh(ip, command):
    async with asyncssh.connect(ip, username="root", known_hosts=None) as conn:
        process = await conn.create_process(command)
        output = ""
        async for line in process.stdout:
            output += line
        await process.wait()
        return output


async def copy_file(ip, local_path, remote_path):
    async with asyncssh.connect(ip, username="root", known_hosts=None) as conn:
        await asyncssh.scp(local_path, (conn, remote_path))


async def apply_caddyfile():
    await copy_file(CADDY_PUBLIC_IP, "./Caddyfile", "/root/Caddyfile")


def generate_caddyfile(instances):
    with open(
        "/root/coderamp/coderamp/coderamp_lib/caddy_templates/caddyfile", "r"
    ) as file:
        caddyfile = file.read()

    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/web") as file:
        web = file.read()
    caddyfile = caddyfile.replace("{web}", web)

    with open("/root/coderamp/coderamp/coderamp_lib/caddy_templates/coderamp") as file:
        coderamp = file.read()

    coderamp_redirects = ""
    for i in instances:

        coderamp_redirects += coderamp.replace("{ip}", f"{i.public_ip}").replace(
            "{uuid}", f"{i.uuid}"
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


CADDY_IP = os.getenv("CADDY_IP")


async def update_caddy(instances):
    generate_caddyfile(instances)
    await apply_caddyfile()
