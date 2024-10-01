import asyncio
import asyncssh
import time
import sys

async def remote_ssh(ip, command):
    async with asyncssh.connect(ip, username='root', known_hosts=None) as conn:
        process = await conn.create_process(command)
        async for line in process.stdout:
            print(line, end='')
        async for line in process.stderr:
            print(line, end='', file=sys.stderr)
        return await process.wait()

async def copy_file(ip, local_path, remote_path):
    async with asyncssh.connect(ip, username='root',known_hosts=None) as conn:
        await asyncssh.scp(local_path, (conn, remote_path))

async def setup_os(ip):
    await remote_ssh(ip, "apt-get install -y zsh")
    await remote_ssh(ip, "mkdir /coderamp")
    await remote_ssh(ip, 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"')

async def setup_code_server(ip):
    await remote_ssh(ip, "curl -fsSL https://code-server.dev/install.sh | sh")
    await copy_file(ip, "./remote_config/code-server@.service", "/lib/systemd/system/code-server@.service")
    await remote_ssh(ip, "sudo systemctl enable --now code-server@root")

async def setup_vscode(ip):
    await remote_ssh(ip, "mkdir /coderamp/.vscode")
    await copy_file(ip, "./remote_config/.vscode/settings.json", "/coderamp/.vscode/settings.json")
    await copy_file(ip, "./remote_config/.vscode/tasks.json", "/coderamp/.vscode/tasks.json")
    await copy_file(ip, "./remote_config/.vscode/favicon.ico", "/usr/lib/code-server/src/browser/media/favicon.ico")


async def setup_user_demo(ip):
    pass

async def wait_for_ssh(ip):
    print("Waiting for ssh...")
    while True:
        try:
            async with asyncssh.connect(ip, username='root',known_hosts=None):
                print(f"SSH ready")
                return
        except:
            await asyncio.sleep(0.5)

async def setup_coderamp(ip):
    await wait_for_ssh(ip)
    await setup_os(ip)
    await setup_code_server(ip)
    await setup_vscode(ip)
    await copy_file(ip, "./remote_config/main.py", "/coderamp/main.py")
