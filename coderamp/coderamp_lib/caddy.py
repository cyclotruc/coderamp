import os
import sys
import asyncio
from dotenv import load_dotenv  
import asyncssh
import json

load_dotenv()   
CADDY_PUBLIC_IP = os.getenv("CADDY_PUBLIC_IP")
CADDY_USERNAME = os.getenv("CADDY_USERNAME")

async def remote_ssh(ip, command):
    async with asyncssh.connect(ip, username='root', known_hosts=None) as conn:
        process = await conn.create_process(command)
        output = ""
        async for line in process.stdout:
            output += line
        await process.wait()
        return output

async def copy_file(ip, local_path, remote_path):
    async with asyncssh.connect(ip, username='root',known_hosts=None) as conn:
        await asyncssh.scp(local_path, (conn, remote_path))


async def get_config(ip):
    curl_command = f"curl 'http://localhost:2019/config/' -H 'Accept: application/json'"
    return await remote_ssh(ip, curl_command)


async def apply_caddyfile(lb_ip):
    await copy_file(lb_ip, './Caddyfile', '/root/Caddyfile')


def generate_caddyfile(redirections):
    with open('/root/coderamp/coderamp/coderamp_lib/caddy_templates/caddyfile', 'r') as file:
        caddyfile = file.read()

    with open('/root/coderamp/coderamp/coderamp_lib/caddy_templates/coderamp') as file:
        coderamp = file.read()
        
    with open('/root/coderamp/coderamp/coderamp_lib/caddy_templates/web') as file:
        web = file.read()

    caddyfile = caddyfile.replace('{web}', web)

    coderamp_redirects = ""
    for i in redirections:
        coderamp_redirects += coderamp.replace("{ip}", redirections[i]).replace("{path}", i)
    
    caddyfile = caddyfile.replace('{coderamps}', coderamp_redirects)

    with open('Caddyfile', 'w') as f:
        f.write(caddyfile)
    return caddyfile


redirections = {}

async def add_redirect(lb_ip, url, dest_ip):
    redirections[url] = f'{dest_ip}:8080'
    
    generate_caddyfile(redirections)
    await apply_caddyfile(lb_ip)


async def main():
    await add_redirect('51.159.179.237', 'test', '157.25.15.62')

if __name__ == "__main__":
    asyncio.run(main())

