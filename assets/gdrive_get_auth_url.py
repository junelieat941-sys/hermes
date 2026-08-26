#!/usr/bin/env python3
"""Google Drive OAuth2 - Generate Auth URL and wait for code"""
import os
import json
import urllib.parse
import urllib.request
import webbrowser
import time
import sys

CLIENT_ID = "AIzaSyC9g28wpuJJ9HWfzmJIGS-X9O9xp6Etj-4"  # This is API key
CRED_FILE = os.path.expanduser("~/.gdrive_credentials.json")

print("="*70)
print("Google Drive Backup - OAuth Authorization")
print("="*70)

# Check for existing credentials
if os.path.exists(CRED_FILE):
    print("\n✓ Found existing credentials!")
    with open(CRED_FILE) as f:
        creds = json.load(f)
    print(f"  Client ID: {creds.get('client_id', 'N/A')[:30]}...")
    if creds.get('refresh_token'):
        print("  Refresh Token: [EXISTS]")
    print("\nYou can skip authorization and proceed to backup.")
    print()
else:
    print("\n⚠ No credentials found.")
    print("\nTo authorize Google Drive, you need OAuth credentials:")
    print("\n1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create OAuth 2.0 Desktop client ID")
    print("3. Download the JSON file")
    print("4. Run: python3 /workspaces/hermes-agent/assets/gdrive_get_auth_url.py --setup")
    print()

print("="*70)
print("OAuth Authorization URL (for manual flow)")
print("="*70)

# If no valid OAuth credentials, show manual instructions
if not CLIENT_ID.endswith('.apps.googleusercontent.com'):
    print("\n✗ Current CLIENT_ID is an API key, not OAuth.")
    print("\nPlease create OAuth credentials first.")
    print("\n" + "="*70)
    print("MANUAL AUTHORIZATION STEPS:")
    print("="*70)
    print("""
1. Go to Google Cloud Console:
   https://console.cloud.google.com/apis/credentials

2. Create OAuth 2.0 Client ID:
   - Application type: Desktop app
   - Name: Hermes Backup
   
3. Download the JSON file

4. Extract these values:
   - client_id (ends with .apps.googleusercontent.com)
   - client_secret (long string)

5. Save to: ~/.gdrive_client_secret.json
   OR set environment variables:
   export GDRIVE_CLIENT_ID="your_client_id"
   export GDRIVE_CLIENT_SECRET="your_client_secret"
""")
    sys.exit(1)

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

print("\nSTEP 1: Open this URL in your browser:")
print("\n" + auth_url + "\n")

print("STEP 2: Sign in and grant permission")
print("STEP 3: Copy the authorization code from URL")
print("        (URL will redirect to: http://localhost:8085/?code=XXXX)")
print()

# Try to open browser
try:
    webbrowser.open(auth_url)
    print("✓ Browser opened automatically.")
except:
    print("Could not open browser automatically.")
    print("Please copy and paste the URL above into your browser.")
print()

# Wait for user to provide code
print("="*70)
print("STEP 4: Enter Authorization Code")
print("="*70)
print("\nPaste the authorization code (after ?code=):")
print("Or just press Enter if you've already authorized and have code")
print()

# For non-interactive mode, use environment variable or file
auth_code = os.environ.get('GDRIVE_AUTH_CODE', '').strip()
if not auth_code and os.path.exists('/tmp/gdrive_auth_code'):
    with open('/tmp/gdrive_auth_code') as f:
        auth_code = f.read().strip()

if auth_code:
    print(f"Using code from environment: {auth_code[:20]}...")
else:
    print("No code provided. Please run with:")
    print(f"  echo 'AUTH_CODE' > /tmp/gdrive_auth_code")
    print(f"  python3 {sys.argv[0]}")
    print()
    print("Or wait for manual input...")
    try:
        auth_code = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\n✗ No authorization code provided.")
        print("\nTo proceed, you need valid OAuth credentials:")
        print(f"  - Save to: {CRED_FILE}")
        print("  - Or set: export GDRIVE_CLIENT_ID=...")
        print("  - Or set: export GDRIVE_CLIENT_SECRET=...")
        sys.exit(1)

if not auth_code:
    print("\n✗ Empty authorization code")
    sys.exit(1)

print("\nExchanging code for tokens...")
try:
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': os.environ.get('GDRIVE_CLIENT_SECRET', ''),
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }).encode()
    
    req = urllib.request.Request(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read().decode())
    
    # Save
    creds = {
        'client_id': CLIENT_ID,
        'client_secret': os.environ.get('GDRIVE_CLIENT_SECRET', ''),
        'refresh_token': tokens['refresh_token'],
        'access_token': tokens.get('access_token', ''),
        'token_expiry': time.time() + tokens.get('expires_in', 3600)
    }
    with open(CRED_FILE, 'w') as f:
        json.dump(creds, f, indent=2)
    
    print(f"\n✓ Credentials saved to {CRED_FILE}")
    print("\nYou can now backup videos to Google Drive!")
    print(f"Run: python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py --backup")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nMake sure:")
    print("- Client secret is correct")
    print("- Authorization code is valid (not expired)")
    print("- You've authorized the correct client ID")
