from fabric import Connection
import time

def remote_ssh(ip, command):
    c = Connection(host=ip, user='root')
    c.run(command)


def copy_file(ip, local_path, remote_path):
    c = Connection(host=ip, user='root')
    c.put(local_path, remote_path)


def setup_os(ip):
    remote_ssh(ip, "apt-get install -y zsh")
    remote_ssh(ip, "mkdir /coderamp")
    remote_ssh(ip, 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"')


def setup_code_server(ip):
    remote_ssh(ip, "curl -fsSL https://code-server.dev/install.sh | sh")
    copy_file(ip, "./remote_config/code-server@.service", "/lib/systemd/system/code-server@.service")
    remote_ssh(ip, "sudo systemctl enable --now code-server@root")
    

def setup_vscode(ip):
    remote_ssh(ip, "mkdir /coderamp/.vscode")
    copy_file(ip, "./remote_config/.vscode/settings.json", "/coderamp/.vscode/settings.json")
    copy_file(ip, "./remote_config/.vscode/tasks.json", "/coderamp/.vscode/tasks.json")

def wait_for_ssh(ip):
    print("Waiting for ssh...")
    ready = False
    while not ready:
        try:
            c = Connection(host=ip, user='root')
            c.run("ls")
            ready = True
        except:
            time.sleep(0.5)
    print(f"SSH ready")


def setup_coderamp(ip):
    wait_for_ssh(ip)
    setup_os(ip)
    setup_code_server(ip)
    setup_vscode(ip)

    copy_file(ip, "./remote_config/main.py", "/coderamp/main.py")