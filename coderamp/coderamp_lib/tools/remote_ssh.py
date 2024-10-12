import asyncio
import asyncssh
import sys


async def run(ip, command):
    async with asyncssh.connect(ip, username="root", known_hosts=None) as conn:
        process = await conn.create_process(command)
        async for line in process.stdout:
            print(line, end="")
        async for line in process.stderr:
            print(line, end="", file=sys.stderr)
        return await process.wait()


async def remote_ssh(ip, command):
    async with asyncssh.connect(ip, username="root", known_hosts=None) as conn:
        process = await conn.create_process(command)
        output = ""
        async for line in process.stdout:
            output += line
        await process.wait()
        return output


async def write_to_file(ip, content, remote_path):
    await remote_ssh(ip, f"echo '{content}' > {remote_path}")


async def copy_file(ip, local_path, remote_path):
    async with asyncssh.connect(ip, username="root", known_hosts=None) as conn:
        await asyncssh.scp(local_path, (conn, remote_path))


async def wait_for_ssh(ip):
    print("Waiting for ssh...", end="")
    while True:
        try:
            async with asyncssh.connect(ip, username="root", known_hosts=None):
                print(f"SSH ready")
                return
        except:
            await asyncio.sleep(0.5)
