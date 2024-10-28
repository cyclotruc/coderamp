from .tools import run, copy_file, write_to_file, wait_for_ssh
from rxconfig import CODERAMP_DOMAIN


async def setup_os(ip):
    await run(ip, "apt-get update")
    await run(ip, "apt-get install -y zsh")
    await run(
        ip,
        'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
    )


async def setup_code_server(ip, domain, extensions):
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

    if extensions:
        for extension in extensions.split(","):
            await run(ip, f"code-server --install-extension {extension}")

    await run(ip, "sudo systemctl enable --now code-server@root")


async def setup_user_demo(ip, repo_url, setup_commands, open_folder):
    await run(ip, f"mkdir {open_folder}")
    if repo_url:
        cmd = f"git clone {repo_url} {open_folder}"
        await run(ip, cmd)
    if setup_commands:
        await write_to_file(ip, setup_commands, "/root/install.sh")
        await run(ip, "bash /root/install.sh")


async def setup_vscode(ip, open_file, open_folder, open_commands):
    await run(ip, "mkdir -p /root/.local/share/code-server/User/")
    with open(
        "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/settings.json"
    ) as file:
        content = file.read()
    await write_to_file(
        ip,
        content,
        f"/root/.local/share/code-server/User/settings.json",
    )
    await run(ip, f"mkdir -p {open_folder}/.vscode")

    # with open(
    #     "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/tasks.json"
    # ) as file:
    #     content = file.read()

    #     content = content.replace("{open_file}", open_file_template).replace(
    #         "{open_commands}", open_commands
    #     )
    # await write_to_file(
    #     ip,
    #     content,
    #     f"{open_folder}/.vscode/tasks.json",
    # )


async def setup_coderamp(instance):
    await wait_for_ssh(instance.public_ip)
    await setup_os(instance.public_ip)
    await setup_code_server(
        instance.public_ip,
        f"{instance.uuid}.{CODERAMP_DOMAIN}/",
        instance.coderamp.extensions,
    )
    print("USER SETUPWITH ", instance.coderamp.setup_commands)
    await setup_user_demo(
        instance.public_ip,
        instance.coderamp.git_url,
        instance.coderamp.setup_commands,
        instance.coderamp.open_folder,
    )
    await setup_vscode(
        instance.public_ip,
        instance.coderamp.open_file,
        instance.coderamp.open_folder,
        instance.coderamp.open_commands,
    )
