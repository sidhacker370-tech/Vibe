import urllib.request
import urllib.parse
import json
import time
import subprocess
import os
import sys
import random

def make_json_request(url, method="GET", token=None, payload=None):
    req = urllib.request.Request(url, method=method)
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    if payload:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(payload).encode()
        return json.loads(urllib.request.urlopen(req, data=data).read().decode())
    else:
        return json.loads(urllib.request.urlopen(req).read().decode())

def login(url, email, password):
    req = urllib.request.Request(f"{url}/login", method="POST")
    data = urllib.parse.urlencode({"username": email, "password": password}).encode()
    return json.loads(urllib.request.urlopen(req, data=data).read().decode()).get("access_token")

# Start server
print("Starting server...")
env = os.environ.copy()
env["SECRET_KEY"] = "super_secret"
server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8009"], cwd="d:/Vibe/backend", env=env)
time.sleep(3)

try:
    BASE_URL = "http://127.0.0.1:8009/api/v1"
    
    print("--- STARTING COMPLETE E2E FLOW ---")
    
    # User 1 (Creator)
    u1 = random.randint(1000, 9999)
    email1 = f"creator_{u1}@test.com"
    pwd = "Password123!"
    make_json_request(f"{BASE_URL}/auth/register", "POST", payload={"username": f"User1_{u1}", "email": email1, "password": pwd})
    token1 = login(f"{BASE_URL}/auth", email1, pwd)
    user1_info = make_json_request(f"{BASE_URL}/auth/me", "GET", token=token1)
    user1_id = user1_info["id"]

    # User 2 (Joiner & Follower)
    u2 = random.randint(1000, 9999)
    email2 = f"joiner_{u2}@test.com"
    make_json_request(f"{BASE_URL}/auth/register", "POST", payload={"username": f"User2_{u2}", "email": email2, "password": pwd})
    token2 = login(f"{BASE_URL}/auth", email2, pwd)

    # 1. Create Vibe
    vibe = make_json_request(f"{BASE_URL}/vibes/", "POST", token=token1, payload={"name": "Testing Vibe", "description": "A vibe for testing"})
    vibe_id = vibe["id"]
    print("1. Created Vibe:", vibe_id)

    # 2. Join Vibe
    make_json_request(f"{BASE_URL}/vibes/{vibe_id}/join", "POST", token=token2, payload={})
    print("2. Joined Vibe!")

    # 3. Post
    post = make_json_request(f"{BASE_URL}/vibes/{vibe_id}/posts", "POST", token=token1, payload={"content": "Hello Vibe!"})
    post_id = post["id"]
    print("3. Created Post:", post_id)

    # 4. Comment
    comment = make_json_request(f"{BASE_URL}/posts/{post_id}/comments", "POST", token=token2, payload={"content": "Nice post!"})
    print("4. Created Comment:", comment["id"])

    # 5. Follow Someone
    make_json_request(f"{BASE_URL}/users/{user1_id}/follow", "POST", token=token2, payload={})
    print("5. Followed User 1!")

    # 6. Receive Notification
    notifs = make_json_request(f"{BASE_URL}/notifications/", "GET", token=token1)
    print("6. Notifications for User 1:", len(notifs))
    for n in notifs:
        print(f"   -> Type: {n['type']}, Read: {n['is_read']}")

    print("--- E2E FLOW SUCCESSFUL ---")

finally:
    server.terminate()
