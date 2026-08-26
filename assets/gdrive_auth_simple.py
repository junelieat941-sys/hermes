#!/usr/bin/env python3
"""
Simple Google Drive OAuth2 Authorization
Usage: Run this script, follow the prompts
"""
import os
import json
import urllib.parse
import urllib.request
import webbrowser
import time

CLIENT_ID = "AIzaSyC9g28wpuJJ9HWfzmJIGS-X9O9xp6Etj-4"  # This is an API key, not OAuth
CRED_FILE = os.path.expanduser("~/.gdrive_credentials.json")

print("""
============================================================
Google Drive Authorization
============================================================

⚠  NOTE: The API key you provided is not valid for OAuth.

API keys (AIza...) are for simple API calls, not for
accessing personal Google Drive files.

For Google Drive access, you need OAuth 2.0 credentials.

============================================================
""")

print("\nSTEP 1: Get OAuth Credentials")
print("-" * 60)
print("""
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create a project (if not exists)
3. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
4. Application type: "Desktop app"
5. Click "CREATE"
6. Download the JSON file
7. Open it and find:
   - client_id: ends with .apps.googleusercontent.com
   - client_secret: long random string
""")

# Check if user has credentials file
json_path = os.path.expanduser("~/.gdrive_client_secret.json")
if os.path.exists(json_path):
    print(f"\n✓ Found credentials at {json_path}")
    with open(json_path) as f:
        data = json.load(f)
    config = data.get('installed', data)
    CLIENT_ID = config['client_id']
    CLIENT_SECRET = config['client_secret']
    print(f"  Client ID: {CLIENT_ID[:30]}...")
else:
    print("\n✗ No credentials file found")
    print(f"  Please save your downloaded JSON as: {json_path}")
    print("\nOr manually enter credentials below:")
    
    # Manual entry
    CLIENT_ID = input("Client ID (ending with .apps.googleusercontent.com): ").strip()
    CLIENT_SECRET = input("Client Secret: ").strip()

# Generate auth URL
SCOPES = "https://www.googleapis.com/auth/drive.file"
REDIRECT_URI = "http://localhost:8085"

params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': SCOPES,
    'access_type': 'offline',
    'prompt': 'consent'
}
auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

print("\n" + "="*60)
print("STEP 2: Authorize")
print("="*60)
print(f"\nOpen this URL in your browser:")
print(auth_url)
print("\nThen paste the authorization code from the URL:")
print("(It will show: https://localhost:8085/?code=4/xxxx...)\n")

input("Press Enter after you've opened the URL...")
webbrowser.open(auth_url)

auth_code = input("Authorization code: ").strip()
if auth_code.startswith('code='):
    auth_code = auth_code[5:]

if not auth_code:
    print("\n✗ No code provided")
    exit(1)

# Exchange for tokens
print("\nExchanging code for tokens...")
token_url = "https://oauth2.googleapis.com/token"
data = urllib.parse.urlencode({
    'code': auth_code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code'
}).encode()

req = urllib.request.Request(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
try:
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read().decode())
    
    # Save credentials
    creds = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': tokens['refresh_token'],
        'access_token': tokens.get('access_token', ''),
        'token_expiry': time.time() + tokens.get('expires_in', 3600)
    }
    with open(CRED_FILE, 'w') as f:
        json.dump(creds, f, indent=2)
    
    print(f"\n✓ Credentials saved to {CRED_FILE}")
    print("\nYou can now use Google Drive backup!")
    print("Run: python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py --backup")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nPossible issues:")
    print("- Invalid authorization code")
    print("- Credentials expired")
    print("- Wrong client_id or client_secret")
