import asyncio
import json
import os
import subprocess
import time

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount the static directory to serve index.html
app.mount("/static", StaticFiles(directory="static"), name="static")


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode('utf-8'), error.decode('utf-8')

def start_coder_server():
    command = "coder server &"
    output, error = run_command(command)
    if error:
        print(f"Error starting Coder server: {error}")
    else:
        print("Coder server started successfully")

start_coder_server()




@app.get("/")
async def read_root():
    with open("static/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("ready")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "button_clicked":
                create_workspace("made-from-python333", "docker-test")
                await websocket.send_text("Button click received!")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()





def login_to_coder(url, username, password):
    # Set environment variables for non-interactive login
    os.environ['CODER_URL'] = url
    os.environ['CODER_SESSION_TOKEN'] = f"gJrCHzLMhx-7UUXUGVfMIFLlgJNDIgG2J"

    command = "coder login --no-open"
    output, error = run_command(command)
    if "error" in output.lower() or error:
        print(f"Error logging in: {error or output}")
        return False
    else:
        print("Logged in successfully")
        return True

def create_workspace(name, template):

    login_to_coder("http://localhost:3000", "test@a.b", "Test.1011")
    command = f"coder create {name} -y --template {template}"
    output, error = run_command(command)
    if error:
        print(f"Error creating workspace: {error}")
    else:
        print(f"Workspace {name} created successfully")
    
    # Create a user
    
    
    # Create a workspace
    



if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)