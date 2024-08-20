import requests
import os
from dotenv import load_dotenv
import time
from fabric import Connection


load_dotenv()
SCW_ACCESS_KEY  = os.getenv("SCW_ACCESS_KEY")
SCW_SECRET_KEY  = os.getenv("SCW_SECRET_KEY")
SCW_DEFAULT_ORGANIZATION_ID  = os.getenv("SCW_DEFAULT_ORGANIZATION_ID")
SCW_DEFAULT_PROJECT_ID   = os.getenv("SCW_DEFAULT_PROJECT_ID")
SCW_DEFAULT_ZONE = os.getenv("SCW_DEFAULT_ZONE")

headers = {
    "Content-Type": "application/json",
    "X-Auth-Token": SCW_SECRET_KEY
}


def get_instance(id):
    url = f"https://api.scaleway.com/instance/v1/zones/{SCW_DEFAULT_ZONE}/servers/{id}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get instance {id} {response.status_code}: {response.json()}")


def start_instance(id):
    url = f"https://api.scaleway.com/instance/v1/zones/{SCW_DEFAULT_ZONE}/servers/{id}/action"
    
    data = {
        "action": "poweron",
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 202:
        print(f"Started instance: {id}")
    else:
        print(f"Failed to start instance {id}, {response.status_code}: {response.json()}")

def terminate_instance(id):
    url = f"https://api.scaleway.com/instance/v1/zones/{SCW_DEFAULT_ZONE}/servers/{id}/action"
    
    data = {
        "action": "terminate",
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 202:
        print(f"Stopped instance: {id}")
    else:
        print(f"Failed to stop instance {id}, {response.status_code}: {response.json()}")


def create_instance(name):
    url = f"https://api.scaleway.com/instance/v1/zones/{SCW_DEFAULT_ZONE}/servers"

    data = {
        "commercial_type": "DEV1-S",
        "image": "77f47c21-772d-4c10-ac97-f5949447df66",
        "name": name,
        "tags": ["codebox",],
        "project": SCW_DEFAULT_PROJECT_ID,
        "routed_ip_enabled": True,
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Successfully created instance:", response.json()['server']['id'])
        return response.json()['server']['id']
    else:
        print(f"Failed to create instance: \n{data}")


def list_instances():
    url = f"https://api.scaleway.com/instance/v1/zones/{SCW_DEFAULT_ZONE}/servers"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        instances = response.json()
        print("Instances:")
        for i in range(len(instances['servers'])):
            print(f"{i}: ({instances['servers'][i]['commercial_type']}) -> {instances['servers'][i]['id']} [{instances['servers'][i]['state']}]")
    else:
        print(f"Failed to list instances: {response.json()}")

def list_codeboxes():
    url = f"https://api.scaleway.com/instance/v1/zones/{SCW_DEFAULT_ZONE}/servers"
    response = requests.get(url, params = {"tags": "codebox"} ,headers=headers)

    if response.status_code == 200:
        instances = response.json()
        ids = []
        print("Codeboxes:")
        for i in range(len(instances['servers'])):
            ids.append(instances['servers'][i]['id'])
            print(f"{i}: ({instances['servers'][i]['commercial_type']}) -> {instances['servers'][i]['id']} [{instances['servers'][i]['state']}]")
        return ids
    else:
        print(f"Failed to list instances: {response.json()}")

def delete_all_codeboxes():
    ids = list_codeboxes()
    for id in ids:
        terminate_instance(id)

def wait_for_ip(id):
    print("Waiting for ip...")
    start = time.time()
    ip = None
    while not ip:
        state = get_instance(id)['server']['public_ip']        
        if state:
            ip = state['address']
        time.sleep(0.1)
    print(f"Found IP after {time.time() - start}")
    return ip


def wait_for_ready(id):
    print("Waiting for ready...")
    start = time.time()
    state = None
    while state != "running":
        state = get_instance(id)['server']['state']        
        time.sleep(0.5)
    print(f"Ready after {time.time() - start}")
    

def wait_for_ssh(ip):
    print("Waiting for ssh...")
    ready = False
    start = time.time()
    while not ready:
        try:
            c = Connection(host=ip, user='root')
            c.run("ls")
            ready = True
        except:
            time.sleep(0.5)
    print(f"SSH ready after {time.time() - start}")


def remote_ssh(ip, command):
    c = Connection(host=ip, user='root')
    result = c.run(command)



def create_file(ip, path, content):
    cmd = f'echo "{content[0]}" > {path}'
    remote_ssh(ip, cmd)
    for line in content[1:]:
        cmd = f'echo "{line}" >> {path}'
        remote_ssh(ip, cmd)

def setup_code_server(ip):
    cmd = "curl -fsSL https://code-server.dev/install.sh | sh"
    remote_ssh(ip, cmd)

    service_config = [
        "[Unit]",
        "Description=code-server",
        "After=network.target",
        "",
        "[Service]",
        "Type=exec",
        "ExecStart=/usr/bin/code-server --bind-addr 0.0.0.0:8080 --auth none",
        "Restart=always",
        "User=%i",
        "",
        "[Install]",
        "WantedBy=default.target",
    ]
    create_file(ip, "/lib/systemd/system/code-server@.service", service_config)

    vsccode_config = [
    
    ]
    cmd = "sudo systemctl enable --now code-server@root"
    remote_ssh(ip, cmd)
    
    

delete_all_codeboxes()

new_id = create_instance("test1")
start_instance(new_id)
wait_for_ready(new_id)
ip = wait_for_ip(new_id)
wait_for_ssh(ip)

setup_code_server(ip)


print(f"http://{new_id}.pub.instances.scw.cloud:8080")