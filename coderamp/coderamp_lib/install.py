import os

from .tools import run, copy_file, write_to_file, wait_for_ssh
from rxconfig import CODERAMP_DOMAIN

# TODO remove all absolute paths


async def setup_os(instance):
    await run(instance.public_ip, "apt-get update")
    await run(instance.public_ip, "apt-get install -y zsh unzip")
    await run(
        instance.public_ip,
        'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
    )
    await run(instance.public_ip, "echo 'alias code=code-server' >> ~/.zshrc")


async def setup_code_server(instance, coderamp):
    await run(instance.public_ip, "curl -fsSL https://code-server.dev/install.sh | sh")
    await copy_file(
        instance.public_ip,
        "/root/coderamp/coderamp/coderamp_lib/remote_config/favicon.ico",
        "/usr/lib/code-server/src/browser/media/favicon.ico",
    )

    with open(
        "/root/coderamp/coderamp/coderamp_lib/remote_config/code-server@.service"
    ) as file:
        content = file.read()
        content = content.replace("{domain}", f"{instance.uuid}.{CODERAMP_DOMAIN}/")
    await write_to_file(
        instance.public_ip,
        content,
        "/lib/systemd/system/code-server@.service",
    )

    if coderamp.extensions:
        for extension in coderamp.extensions.split(","):
            await run(
                instance.public_ip, f"code-server --install-extension {extension}"
            )

    await run(instance.public_ip, "sudo systemctl enable --now code-server@root")


async def setup_user_demo(instance, coderamp):
    await run(instance.public_ip, f"mkdir {coderamp.workspace_folder}")
    if coderamp.git_url:
        cmd = f"git clone {coderamp.git_url} {coderamp.workspace_folder}"
        await run(instance.public_ip, cmd)
    if coderamp.setup_commands:
        setup_commands = coderamp.setup_commands.replace(
            "{uuid}", str(instance.uuid)
        ).replace("{domain}", CODERAMP_DOMAIN)
        await write_to_file(instance.public_ip, setup_commands, "/root/install.sh")
        await run(instance.public_ip, "bash /root/install.sh", verbose=True)


async def setup_tasks(instance, coderamp):

    if coderamp.open_file or coderamp.open_commands:
        with open(
            "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/tasks.json"
        ) as file:
            task_content = file.read()

        if coderamp.open_file:
            path = os.path.dirname(coderamp.open_file)

            await run(instance.public_ip, f"mkdir -p {path}")
            await run(instance.public_ip, f"touch {coderamp.open_file}")

            with open(
                "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/open_file"
            ) as file:
                open_file_template = file.read().replace(
                    "{open_file}", coderamp.open_file
                )

            task_content = task_content.replace("//open_file", open_file_template)

        if coderamp.open_commands:
            with open(
                "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/open_commands"
            ) as file:
                open_commands_template = file.read().replace(
                    "{open_commands}", coderamp.open_commands
                )

            task_content = task_content.replace(
                "//open_commands", open_commands_template
            )

    await run(instance.public_ip, f"mkdir -p {coderamp.workspace_folder}/.vscode")
    await write_to_file(
        instance.public_ip,
        task_content,
        f"{coderamp.workspace_folder}/.vscode/tasks.json",
    )


async def setup_vscode(instance, coderamp):
    await run(instance.public_ip, "mkdir -p /root/.local/share/code-server/User/")
    with open(
        "/root/coderamp/coderamp/coderamp_lib/remote_config/.vscode/settings.json"
    ) as file:
        content = file.read()
    await write_to_file(
        instance.public_ip,
        content,
        f"/root/.local/share/code-server/User/settings.json",
    )

    if coderamp.open_file or coderamp.open_commands:
        await setup_tasks(instance, coderamp)


async def setup_coderamp(instance):
    await wait_for_ssh(instance.public_ip)
    await setup_os(instance)
    await setup_code_server(instance, instance.coderamp)
    await setup_user_demo(instance, instance.coderamp)
    await setup_vscode(instance, instance.coderamp)

    print(f"New [{instance.coderamp.name}] instance is ready")
