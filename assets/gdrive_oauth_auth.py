#!/usr/bin/env python3
"""Google Drive OAuth2 Authorization - Interactive Flow"""
import os
import json
import http.server
import socketserver
import threading
import urllib.parse
import urllib.request
import webbrowser
import time
import sys

REDIRECT_URI = "http://localhost:8085"
SCOPES = "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata"
CRED_FILE = os.path.expanduser("~/.gdrive_credentials.json")

def get_client_config():
    """Prompt user for client ID and secret"""
    print("\n" + "="*60)
    print("Google Drive OAuth2 Authorization")
    print("="*60)
    print("\nYou need Google OAuth credentials:")
    print("\nSTEP 1: Get Client ID and Secret")
    print("-"*60)
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create a new project (or select existing)")
    print("3. Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("4. Application type: 'Desktop app'")
    print("5. Name: 'Hermes Backup'")
    print("6. Click 'CREATE'")
    print("7. Download the JSON (click download icon)")
    print("\nSTEP 2: Extract Client ID and Secret")
    print("-"*60)
    print("Open the downloaded JSON file, find:")
    print("  'client_id': 'YOUR_CLIENT_ID.apps.googleusercontent.com'")
    print("  'client_secret': 'YOUR_CLIENT_SECRET'")
    print("\nOr you can paste the entire JSON path and I'll extract it.")
    print("\n" + "="*60)
    
    # Ask for JSON file path
    json_path = input("Paste the path to downloaded JSON file (or press Enter to skip): ").strip()
    
    if json_path and os.path.exists(json_path):
        try:
            with open(json_path) as f:
                data = json.load(f)
            config = data.get('installed', data)
            client_id = config['client_id']
            client_secret = config['client_secret']
            print(f"\n✓ Loaded credentials from {json_path}")
            print(f"  Client ID: {client_id[:30]}...")
        except Exception as e:
            print(f"\n✗ Error reading JSON: {e}")
            print("Please try again.")
            sys.exit(1)
    else:
        print("\nNo JSON file provided. Please enter credentials manually:")
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()
        
        if not client_id.startswith('YOUR_CLIENT_ID') and 'apps.googleusercontent.com' not in client_id:
            # Try to validate
            if not client_id.endswith('.apps.googleusercontent.com'):
                print("\n⚠ Warning: Client ID doesn't look valid")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    sys.exit(0)
    
    return client_id, client_secret

def generate_auth_url(client_id):
    """Generate OAuth authorization URL"""
    params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPES,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

def exchange_code(auth_code, client_id, client_secret):
    """Exchange authorization code for tokens"""
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }).encode()
    
    req = urllib.request.Request(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def save_credentials(tokens, client_id, client_secret):
    """Save OAuth tokens to file"""
    creds = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': tokens['refresh_token'],
        'access_token': tokens.get('access_token', ''),
        'token_expiry': time.time() + tokens.get('expires_in', 3600)
    }
    with open(CRED_FILE, 'w') as f:
        json.dump(creds, f, indent=2)
    print(f"\n✓ Credentials saved to {CRED_FILE}")

def main():
    # Get client credentials
    client_id, client_secret = get_client_config()
    
    # Generate auth URL
    auth_url = generate_auth_url(client_id)
    
    print("\n" + "="*60)
    print("STEP 3: Authorize in Browser")
    print("="*60)
    print(f"\n1. Open this URL in your browser:")
    print(f"\n   {auth_url}\n")
    print("2. Sign in to your Google account")
    print("3. Click 'Allow' to grant permissions")
    print("4. You'll see an error page (this is normal)")
    print("5. Copy the authorization code from the URL")
    print("   (It will look like: ?code=4/xxx...)\n")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("✓ Opened browser automatically")
    except:
        print("Could not open browser automatically")
    
    print("\n" + "="*60)
    print("STEP 4: Enter Authorization Code")
    print("="*60)
    
    # Wait for user input
    auth_code = input("\nPaste the authorization code here: ").strip()
    
    if not auth_code or auth_code.startswith('?code='):
        if auth_code.startswith('?code='):
            auth_code = auth_code[6:]  # Remove prefix
    
    if not auth_code:
        print("\n✗ No authorization code provided")
        sys.exit(1)
    
    # Exchange code for tokens
    print("\nExchanging code for tokens...")
    try:
        tokens = exchange_code(auth_code, client_id, client_secret)
        save_credentials(tokens, client_id, client_secret)
        print("\n" + "="*60)
        print("✓ Authorization successful!")
        print("="*60)
        print(f"\nYou can now backup videos to Google Drive:")
        print(f"  python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py --backup")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
