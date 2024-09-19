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

async def get_config(ip):
    curl_command = f"curl 'http://localhost:2019/config/' -H 'Accept: application/json'"
    return await remote_ssh(ip, curl_command)


def generate_caddyfile(redirections):
    with open('./caddy_templates/caddyfile', 'r') as file:
        caddyfile = file.read()

    with open('./caddy_templates/coderamp') as file:
        coderamp = file.read()
        
    with open('./caddy_templates/web') as file:
        web = file.read()

    caddyfile = caddyfile.replace('{web}', web)

    coderamp_redirects = ""
    for i in redirections:
        coderamp_redirects += coderamp.replace("{ip}", redirections[i]).replace("{path}", i)
    
    caddyfile = caddyfile.replace('{coderamps}', coderamp_redirects)

    return caddyfile




async def main():
    redirections = {
        "supernouvelleurl": "157.25.15.62:8080"

    }
    
    a = generate_caddyfile(redirections)
    print(a)

if __name__ == "__main__":
    asyncio.run(main())

