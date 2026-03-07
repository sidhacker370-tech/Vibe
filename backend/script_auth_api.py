import urllib.request
import urllib.parse
import json
import time
import subprocess
import os
import sys

# Start the uvicorn server
server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8008"], cwd="d:/Vibe/backend")
time.sleep(3) # Wait for startup

try:
    base_url = "http://127.0.0.1:8008/api/v1/auth"

    # Register
    req = urllib.request.Request(f"{base_url}/register", method="POST")
    req.add_header('Content-Type', 'application/json')
    data = json.dumps({"username": "testuser1", "email": "test1@vibe.com", "password": "Password123!"}).encode()
    try:
        with urllib.request.urlopen(req, data=data) as f:
            print("Register:", f.status, f.read().decode())
    except urllib.error.HTTPError as e:
        print("Register existing/error:", e.code, e.read().decode())

    # Login
    req = urllib.request.Request(f"{base_url}/login", method="POST")
    data = urllib.parse.urlencode({"username": "test1@vibe.com", "password": "Password123!"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        log_res = f.read().decode()
        print("Login:", f.status, log_res)
        token = json.loads(log_res).get("access_token")

    # Me
    req = urllib.request.Request(f"{base_url}/me", method="GET")
    req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as f:
        print("Me:", f.status, f.read().decode())

finally:
    server.terminate()
