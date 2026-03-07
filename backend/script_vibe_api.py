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

    # Make a random user
    rand_user = f"user_{random.randint(1000, 9999)}"
    email = f"{rand_user}@vibe.com"

    # Register
    req = urllib.request.Request(f"{auth_url}/register", method="POST")
    req.add_header('Content-Type', 'application/json')
    data = json.dumps({"username": rand_user, "email": email, "password": "Password123!"}).encode()
    urllib.request.urlopen(req, data=data)

    # Login
    req = urllib.request.Request(f"{auth_url}/login", method="POST")
    data = urllib.parse.urlencode({"username": email, "password": "Password123!"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        log_res = f.read().decode()
        token = json.loads(log_res).get("access_token")

    # Create Vibe
    req = urllib.request.Request(f"{vibe_url}/", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    data = json.dumps({"name": f"Vibe of {rand_user}", "description": "Chill room"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        vibe_res = f.read().decode()
        vibe_id = json.loads(vibe_res).get("id")

    # [Test 1] Create Posts
    for i in range(5):
        req = urllib.request.Request(f"{vibe_url}/{vibe_id}/posts", method="POST")
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')
        data = json.dumps({"content": f"Message test {i}"}).encode()
        with urllib.request.urlopen(req, data=data) as f:
            print(f"Post {i} created:", f.status)

    # [Test 2] Get Posts (Paginated) - limit 2
    req = urllib.request.Request(f"{vibe_url}/{vibe_id}/posts?limit=2", method="GET")
    req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as f:
        page_1 = json.loads(f.read().decode())
        print("Page 1 length:", len(page_1["items"]))
        print("Contents:", [p["content"] for p in page_1["items"]])
        next_cursor = page_1["next_cursor"]
        print("Next cursor:", next_cursor)

    # [Test 3] Get Posts Page 2
    encoded_cursor = urllib.parse.quote(next_cursor)
    req = urllib.request.Request(f"{vibe_url}/{vibe_id}/posts?limit=2&cursor={encoded_cursor}", method="GET")
    req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as f:
        page_2 = json.loads(f.read().decode())
        print("Page 2 length:", len(page_2["items"]))
        print("Contents:", [p["content"] for p in page_2["items"]])

finally:
    server.terminate()
