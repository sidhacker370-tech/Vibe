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
    base_url = "http://127.0.0.1:8008/api/v1"
    
    def register_and_login(username):
        username = f"{username}_{random.randint(1000, 9999)}"
        email = f"{username}@vibe.com"
        # Register
        req = urllib.request.Request(f"{base_url}/auth/register", method="POST")
        req.add_header('Content-Type', 'application/json')
        urllib.request.urlopen(req, data=json.dumps({"username": username, "email": email, "password": "Password123!"}).encode())
        
        # Login
        req = urllib.request.Request(f"{base_url}/auth/login", method="POST")
        data = urllib.parse.urlencode({"username": email, "password": "Password123!"}).encode()
        with urllib.request.urlopen(req, data=data) as f:
            log_res = json.loads(f.read().decode())
            return log_res.get("access_token"), log_res.get("user", {}).get("id")

    # We need user IDs. Let's decode them from token or just get from /me
    def get_me(token):
        req = urllib.request.Request(f"{base_url}/auth/me", method="GET")
        req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req) as f:
            return json.loads(f.read().decode())

    # Create users
    token_a, _ = register_and_login("AliceFeed")
    user_a = get_me(token_a)["id"]
    
    token_b, _ = register_and_login("BobFeed")
    user_b = get_me(token_b)["id"]
    
    token_c, _ = register_and_login("CharlieFeed")
    user_c = get_me(token_c)["id"]

    print(f"Users created: A({user_a}), B({user_b}), C({user_c})")

    # Bob creates a vibe and posts
    req = urllib.request.Request(f"{base_url}/vibes/", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token_b}')
    data = json.dumps({"name": "Bob's Code Lounge", "description": "Bob rules"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        vibe_b_id = json.loads(f.read().decode()).get("id")

    # Bob posts in his vibe
    req = urllib.request.Request(f"{base_url}/vibes/{vibe_b_id}/posts", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token_b}')
    urllib.request.urlopen(req, data=json.dumps({"content": "Hello from Bob!"}).encode())

    # Charlie creates a vibe and posts
    req = urllib.request.Request(f"{base_url}/vibes/", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token_c}')
    data = json.dumps({"name": "Charlie's Art Studio", "description": "Drawings"}).encode()
    with urllib.request.urlopen(req, data=data) as f:
        vibe_c_id = json.loads(f.read().decode()).get("id")

    req = urllib.request.Request(f"{base_url}/vibes/{vibe_c_id}/posts", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token_c}')
    urllib.request.urlopen(req, data=json.dumps({"content": "Hello from Charlie!"}).encode())

    # Alice follows Bob
    print("Alice follows Bob...")
    req = urllib.request.Request(f"{base_url}/users/{user_b}/follow", method="POST")
    req.add_header('Authorization', f'Bearer {token_a}')
    with urllib.request.urlopen(req, data=b'') as f:
        print("Follow status:", f.status)

    # Alice joins Charlie's vibe
    print("Alice joins Charlie's Vibe...")
    req = urllib.request.Request(f"{base_url}/vibes/{vibe_c_id}/join", method="POST")
    req.add_header('Authorization', f'Bearer {token_a}')
    with urllib.request.urlopen(req, data=b'') as f:
        print("Join status:", f.status)

    # Alice gets her feed
    print("Alice fetching feed...")
    req = urllib.request.Request(f"{base_url}/feed", method="GET")
    req.add_header('Authorization', f'Bearer {token_a}')
    with urllib.request.urlopen(req) as f:
        feed_data = json.loads(f.read().decode())
        items = feed_data["items"]
        print("Feed length:", len(items))
        for post in items:
            print(f" -> Post by {post['user_id']} in Vibe {post['vibe_id']}: {post['content']}")
            
        assert len(items) == 2, "Alice should see 2 posts (1 from joined vibe, 1 from followed user)"

    # Alice unfollows Bob
    print("Alice unfollows Bob...")
    req = urllib.request.Request(f"{base_url}/users/{user_b}/follow", method="DELETE")
    req.add_header('Authorization', f'Bearer {token_a}')
    with urllib.request.urlopen(req) as f:
        print("Unfollow status:", f.status)

    # Alice gets feed again
    req = urllib.request.Request(f"{base_url}/feed", method="GET")
    req.add_header('Authorization', f'Bearer {token_a}')
    with urllib.request.urlopen(req) as f:
        feed_data = json.loads(f.read().decode())
        items = feed_data["items"]
        print("Feed length after unfollow:", len(items))
        assert len(items) == 1, "Alice should only see Charlie's post now"

    print("SUCCESS: Follow, Unfollow, and Feed Aggregation behaves exactly as intended.")

finally:
    server.terminate()
