from .tools import run, copy_file, write_to_file, wait_for_ssh
from rxconfig import CODERAMP_DOMAIN


async def setup_os(ip):
    await run(ip, "apt-get update")
    await run(ip, "apt-get install -y zsh")
    await run(ip, "apt-get install -y python3-pip")
    await run(ip, "mkdir /coderamp")
    await run(
        ip,
        'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
    )


async def setup_code_server(ip, domain):
    await run(ip, "curl -fsSL https://code-server.dev/install.sh | sh")
    await copy_file(
        ip,
        "/root/coderamp/coderamp/coderamp_lib/remote_config/favicon.ico",
        "/usr/lib/code-server/src/browser/media/favicon.ico",
    )

    with open(
        "/root/coderamp/coderamp/coderamp_lib/remote_config/code-server@.service"
    ) as file:
        content = file.read()
        content = content.replace("{domain}", domain)
    await write_to_file(
        ip,
        content,
        "/lib/systemd/system/code-server@.service",
    )

    await run(ip, "sudo systemctl enable --now code-server@root")


async def setup_user_demo(ip, repo_url, setup_commands):
    if repo_url:
        cmd = f"git clone {repo_url} /coderamp"
        await run(ip, cmd)
    for command in setup_commands.split("\n"):
        await run(ip, command)


async def setup_vscode(ip, open_file, open_folder):
    await run(ip, "mkdir /coderamp/.vscode")
    await copy_file(
        ip,
        "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/settings.json",
        f"{open_folder}/.vscode/settings.json",
    )
    with open(
        "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/tasks.json"
    ) as file:
        content = file.read()
        content = content.replace("{open_file}", open_file)
    await write_to_file(
        ip,
        content,
        f"{open_folder}/.vscode/tasks.json",
    )


async def setup_coderamp(instance):
    await wait_for_ssh(instance.public_ip)
    await setup_os(instance.public_ip)
    await setup_code_server(
        instance.public_ip,
        f"{instance.uuid}.{CODERAMP_DOMAIN}/",
    )
    print("USER SETUPWITH ", instance.coderamp.setup_commands)
    await setup_user_demo(
        instance.public_ip, instance.coderamp.git_url, instance.coderamp.setup_commands
    )
    await setup_vscode(
        instance.public_ip, instance.coderamp.open_file, instance.coderamp.open_folder
    )
