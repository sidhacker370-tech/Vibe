import urllib.request
import urllib.parse
import json
import time
import subprocess
import os
import sys
import random

# Start the uvicorn server
server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8008"], cwd="d:/Vibe/backend")
time.sleep(3) # Wait for startup

try:
    auth_url = "http://127.0.0.1:8008/api/v1/auth"
    vibe_url = "http://127.0.0.1:8008/api/v1/vibes"

    print("--- STARTING E2E JOURNEY ---")

    # ====== USER 1: Creates the Vibe ======
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
    data = json.dumps({"name": "End-To-End Test Vibe", "description": "Testing the flow"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        vibe_id = json.loads(f.read().decode()).get("id")
        print("1. User 1 Created Vibe (ID:", vibe_id, ")")

    # ====== USER 2: The E2E Flow test ======
    u2_int = random.randint(10000, 99999)
    user2_email = f"joiner_{u2_int}@vibe.com"
    user2_name = f"JoinerAlice_{u2_int}"

    # [PHASE 1] Register user
    req = urllib.request.Request(f"{auth_url}/register", method="POST")
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, data=json.dumps({"username": user2_name, "email": user2_email, "password": "Password123!"}).encode()) as f:
        print("2. Register User 2 (Status:", f.status, ")")

    # [PHASE 1.5] Login user
    req = urllib.request.Request(f"{auth_url}/login", method="POST")
    data = urllib.parse.urlencode({"username": user2_email, "password": "Password123!"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        token2 = json.loads(f.read().decode()).get("access_token")

    # [PHASE 2] Join vibe
    req = urllib.request.Request(f"{vibe_url}/{vibe_id}/join", method="POST")
    req.add_header('Authorization', f'Bearer {token2}')
    with urllib.request.urlopen(req, data=b'') as f:
        print("3. Join Vibe as User 2 (Status:", f.status, ")")

    # [PHASE 3] Post inside vibe
    for i in range(1, 4):
        req = urllib.request.Request(f"{vibe_url}/{vibe_id}/posts", method="POST")
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token2}')
        data = json.dumps({"content": f"Hello from E2E Flow! message {i}"}).encode()
        with urllib.request.urlopen(req, data=data) as f:
            pass
    print("4. Created 3 Posts inside Vibe natively")

    # [PHASE 4] Fetch posts
    req = urllib.request.Request(f"{vibe_url}/{vibe_id}/posts", method="GET")
    req.add_header('Authorization', f'Bearer {token2}')
    with urllib.request.urlopen(req) as f:
        posts_data = json.loads(f.read().decode())
        items = posts_data["items"]
        print("5. Fetched Posts array successfully, length:", len(items))
        for post in items:
            print("   ->", post["content"])

    print("\nMVP BACKEND ACHIEVED! THE FLOW IS PERFECT!")

finally:
    server.terminate()
