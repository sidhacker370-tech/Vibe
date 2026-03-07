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

    u1_int = random.randint(10000, 99999)
    user1_email = f"creator_{u1_int}@vibe.com"
    user1_name = f"CreatorBob_{u1_int}"
    
    # Register User 1
    req = urllib.request.Request(f"{auth_url}/register", method="POST")
    req.add_header('Content-Type', 'application/json')
    urllib.request.urlopen(req, data=json.dumps({"username": user1_name, "email": user1_email, "password": "Password123!"}).encode())

    # Login User 1
    req = urllib.request.Request(f"{auth_url}/login", method="POST")
    data = urllib.parse.urlencode({"username": user1_email, "password": "Password123!"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        token1 = json.loads(f.read().decode()).get("access_token")

    # Create Vibe
    req = urllib.request.Request(f"{vibe_url}/", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token1}')
    data = json.dumps({"name": "Realtime WS Chat Vibe", "description": "Testing the WS Room"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        vibe_id = json.loads(f.read().decode()).get("id")
        
    return token1, vibe_id, user1_name

async def test_websocket_chat(token: str, vibe_id: str, username: str):
    ws_url = f"ws://127.0.0.1:8008/api/v1/chat/{vibe_id}?token={token}"
    
    print("Initiating WebSocket connection to:", ws_url)
    async with websockets.connect(ws_url) as websocket:
        print("Connected effectively to", vibe_id)
        
        # Send a message
        msg_payload = "I am a real-time message generated from the test script!"
        print("Emitting payload...")
        await websocket.send(msg_payload)
        
        # Receive the broadcast 
        responseJSONtext = await websocket.recv()
        # Decode broadcast dict
        data = json.loads(responseJSONtext)
        
        print("Received Broadcast:", json.dumps(data, indent=2))
        assert data["content"] == msg_payload
        assert data["username"] == username
        print("SUCCESS! Real-Time Single-Node WebSocket Chat acts efficiently!")

if __name__ == "__main__":
    # Start the uvicorn server
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8008"], cwd="d:/Vibe/backend")
    time.sleep(3) # Wait for startup
    
    try:
        tkn, vid, unm = pre_flight()
        asyncio.run(test_websocket_chat(tkn, vid, unm))
    except Exception as e:
        print("Something failed natively:", str(e))
    finally:
        server.terminate()
