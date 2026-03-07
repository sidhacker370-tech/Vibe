import urllib.request
import urllib.parse
import json
import time
import subprocess
import os
import sys
import random
import asyncio
import websockets

def pre_flight():
    auth_url = "http://127.0.0.1:8008/api/v1/auth"
    vibe_url = "http://127.0.0.1:8008/api/v1/vibes"

    # User A
    uA_int = random.randint(10000, 99999)
    email_a = f"A_{uA_int}@vibe.com"
    name_a = f"Browser_A_{uA_int}"
    # Register & Login User A
    req = urllib.request.Request(f"{auth_url}/register", method="POST")
    req.add_header('Content-Type', 'application/json')
    urllib.request.urlopen(req, data=json.dumps({"username": name_a, "email": email_a, "password": "Password123!"}).encode())

    req = urllib.request.Request(f"{auth_url}/login", method="POST")
    with urllib.request.urlopen(req, data=urllib.parse.urlencode({"username": email_a, "password": "Password123!"}).encode()) as f:
        token_a = json.loads(f.read().decode()).get("access_token")

    # User B
    uB_int = random.randint(10000, 99999)
    email_b = f"B_{uB_int}@vibe.com"
    name_b = f"Browser_B_{uB_int}"
    # Register & Login User B
    req = urllib.request.Request(f"{auth_url}/register", method="POST")
    req.add_header('Content-Type', 'application/json')
    urllib.request.urlopen(req, data=json.dumps({"username": name_b, "email": email_b, "password": "Password123!"}).encode())

    req = urllib.request.Request(f"{auth_url}/login", method="POST")
    with urllib.request.urlopen(req, data=urllib.parse.urlencode({"username": email_b, "password": "Password123!"}).encode()) as f:
        token_b = json.loads(f.read().decode()).get("access_token")

    # Create Vibe using User A
    req = urllib.request.Request(f"{vibe_url}/", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token_a}')
    data = json.dumps({"name": "Core WebSocket Broadcast Room", "description": "Testing the WS broadcasts"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        vibe_id = json.loads(f.read().decode()).get("id")

    # User B Joins the Vibe
    req = urllib.request.Request(f"{vibe_url}/{vibe_id}/join", method="POST")
    req.add_header('Authorization', f'Bearer {token_b}')
    urllib.request.urlopen(req, data=b'')
        
    return token_a, token_b, vibe_id, name_a, name_b


async def browser_a_task(token, vibe_id, name):
    ws_url = f"ws://127.0.0.1:8008/ws/vibes/{vibe_id}?token={token}"
    async with websockets.connect(ws_url) as ws:
        print("[Tab A] Connected")
        await asyncio.sleep(1) # wait for Tab B to stabilize
        print("[Tab A] Sending message...")
        await ws.send("Hello Tab B, this is Tab A broadcasting!")
        
        # also await its own echo back
        echo = json.loads(await ws.recv())
        print("[Tab A] Received back my own message via DB Broadcast:", echo["content"])

async def browser_b_task(token, vibe_id, name):
    ws_url = f"ws://127.0.0.1:8008/ws/vibes/{vibe_id}?token={token}"
    async with websockets.connect(ws_url) as ws:
        print("[Tab B] Connected, waiting for traffic...")
        
        # Listen for Tab A's broadcast
        msgJSON = await ws.recv()
        data = json.loads(msgJSON)
        print("[Tab B] RECEIVED BROADCAST FROM TAB A:", json.dumps(data, indent=2))
        assert data["content"] == "Hello Tab B, this is Tab A broadcasting!"

async def run_2_tabs(ta, tb, vid, na, nb):
    b1_task = asyncio.create_task(browser_b_task(tb, vid, nb))
    await asyncio.sleep(0.5)
    a1_task = asyncio.create_task(browser_a_task(ta, vid, na))
    
    await asyncio.gather(b1_task, a1_task)


if __name__ == "__main__":
    # Start the uvicorn server
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8008"], cwd="d:/Vibe/backend")
    time.sleep(3) # Wait for startup
    
    try:
        ta, tb, vid, na, nb = pre_flight()
        asyncio.run(run_2_tabs(ta, tb, vid, na, nb))
        print("\n🚀 SUCCESS! 2-TAB WEBSOCKET BROADCAST ARCHITECTURE IS FULLY FUNCTIONAL!")
    except Exception as e:
        print("Something failed natively:", str(e))
    finally:
        server.terminate()
