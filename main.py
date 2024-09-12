from fastapi import FastAPI
from fastapi.responses import HTMLResponse



app = FastAPI()


@app.get("/")
async def read_root():
    html_content = """
   <!DOCTYPE html>
<html>
<head>
    <title>Codebox - One-click browser-based dev environments</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            font-size: 36px;
            margin-top: 50px;
            margin-bottom: 20px;
        }
        p {
            font-size: 18px;
            line-height: 1.5;
            margin-bottom: 30px;
        }
        .cta-button {
            display: inline-block;
            padding: 10px 20px;
            font-size: 18px;
            background-color: #007bff;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Codebox</h1>
        <p>Codebox is a one-click browser-based dev environment that lets you spin up a fully-featured development environment in seconds.</p>
        
        <p>Try Codebox</p>
        <a href="https://codesandboxbeta.cloud/code/?folder=/coderamp" class="cta-button">Launch Codebox</a>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)
