import os
import pty
import select
import subprocess
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# واجهة HTML بداخلها مكتبات Xterm.js من CDN
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Web Terminal</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/xterm/5.3.0/xterm.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xterm/5.3.0/xterm.min.js"></script>
    <style>
        body { background-color: #1e1e1e; margin: 0; padding: 10px; }
        #terminal { width: 100vw; height: 98vh; }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <script>
        const term = new Terminal({ cursorBlink: true, fontSize: 14 });
        term.open(document.getElementById('terminal'));
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        ws.onmessage = (event) => term.write(event.data);
        term.onData((data) => ws.send(data));
    </script>
</body>
</html>
"""

@app.get("/")
async def get_index():
    return HTMLResponse(HTML_CONTENT)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # إنشاء Pseudo-terminal (PTY) لربط Bash
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(
        ["/bin/bash"],
        preexec_fn=os.setsid,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        universal_newlines=False
    )
    os.close(slave_fd)

    loop = asyncio.get_running_loop()

    # قراءة المخرجات من الـ PTY وإرسالها إلى الـ WebSocket
    async def read_from_pty():
        try:
            while True:
                await asyncio.sleep(0.01)
                r, _, _ = select.select([master_fd], [], [], 0)
                if master_fd in r:
                    output = os.read(master_fd, 1024)
                    if output:
                        await websocket.send_text(output.decode("utf-8", errors="ignore"))
        except Exception:
            pass

    read_task = asyncio.create_task(read_from_pty())

    try:
        while True:
            # استقبال الأوامر من المتصفح وكتابتها في الـ PTY
            data = await websocket.receive_text()
            os.write(master_fd, data.encode("utf-8"))
    except WebSocketDisconnect:
        read_task.cancel()
        proc.kill()
        os.close(master_fd)
