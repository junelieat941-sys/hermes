#!/usr/bin/env python3
"""
Google Drive OAuth2 Authorization and Video Backup
Usage: python3 backup_to_gdrive.py [--auth]
"""
import os
import sys
import json
import urllib.parse
import urllib.request
import http.server
import socketserver
import threading
import webbrowser
import time

CLIENT_SECRET_PATH = os.path.expanduser("~/.gdrive_client_secret.json")
CRED_FILE = os.path.expanduser("~/.gdrive_credentials.json")
AUTH_SUCCESS_FILE = os.path.expanduser("~/.gdrive_auth_success")

REDIRECT_URI = "http://localhost:8085"
SCOPES = "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata"

class AuthServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if 'code' in params:
            with open(AUTH_SUCCESS_FILE, 'w') as f:
                f.write(params['code'][0])
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h3>Authorization successful!</h3><p>You can close this window.</p></body></html>')
        elif 'error' in params:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f'<html><body><h3>Error: {params["error"][0]}</h3></body></html>'.encode())
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def get_client_config():
    """Load OAuth client configuration"""
    if not os.path.exists(CLIENT_SECRET_PATH):
        print(f"Error: Client secret not found at {CLIENT_SECRET_PATH}")
        print("\nPlease create Google OAuth credentials:")
        print("1. https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Desktop client ID")
        print(f"3. Save JSON to {CLIENT_SECRET_PATH}")
        sys.exit(1)
    
    with open(CLIENT_SECRET_PATH) as f:
        data = json.load(f)
    return data.get('installed', data)

def get_auth_url(client_id):
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

def exchange_code(code, client_id, client_secret):
    """Exchange authorization code for tokens"""
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'code': code,
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
    print(f"Credentials saved to {CRED_FILE}")

def run_auth_flow():
    """Run the OAuth authorization flow"""
    print("Starting Google Drive authorization...")
    
    config = get_client_config()
    client_id = config['client_id']
    client_secret = config['client_secret']
    
    # Start auth server
    server = socketserver.TCPServer(("localhost", 8085), AuthServer)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    # Get auth URL
    auth_url = get_auth_url(client_id)
    print(f"\nPlease visit this URL to authorize:")
    print(auth_url)
    print("\nOr pressing Enter will open it automatically...")
    input()
    webbrowser.open(auth_url)
    
    print("\nWaiting for authorization...")
    print("(Complete the Google sign-in and permission grant in your browser)")
    
    # Wait for auth code
    for i in range(120):  # Wait up to 2 minutes
        if os.path.exists(AUTH_SUCCESS_FILE):
            with open(AUTH_SUCCESS_FILE) as f:
                auth_code = f.read().strip()
            os.remove(AUTH_SUCCESS_FILE)
            break
        time.sleep(1)
    else:
        print("\nTimeout waiting for authorization")
        sys.exit(1)
    
    print("\nExchanging code for tokens...")
    tokens = exchange_code(auth_code, client_id, client_secret)
    save_credentials(tokens, client_id, client_secret)
    
    server.shutdown()
    print("\nAuthorization complete!")

def backup_videos():
    """Backup videos to Google Drive"""
    print("Starting video backup to Google Drive...")
    
    # Check credentials
    if not os.path.exists(CRED_FILE):
        print("No credentials found. Please run authorization first.")
        run_auth_flow()
    
    # Load credentials
    with open(CRED_FILE) as f:
        creds = json.load(f)
    
    client_id = creds['client_id']
    client_secret = creds['client_secret']
    refresh_token = creds['refresh_token']
    
    # Get access token
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode()
    req = urllib.request.Request(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read().decode())
        access_token = tokens['access_token']
    
    # Find videos to backup
    assets_dir = "/workspaces/hermes-agent/assets"
    videos = []
    for f in os.listdir(assets_dir):
        if f.endswith('.mp4') and 'final' in f:
            videos.append(os.path.join(assets_dir, f))
    
    print(f"Found {len(videos)} videos to backup")
    
    # Upload each video
    for video_path in sorted(videos):
        file_name = os.path.basename(video_path)
        file_size = os.path.getsize(video_path)
        print(f"\nUploading: {file_name} ({file_size/1024/1024:.1f} MB)")
        
        # Read file and upload
        with open(video_path, 'rb') as f:
            data = f.read()
        
        upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
        req = urllib.request.Request(upload_url, data=data, method='POST')
        req.add_header('Authorization', f'Bearer {access_token}')
        req.add_header('Content-Type', 'video/mp4')
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            print(f"  Uploaded: https://drive.google.com/file/d/{result['id']}/view")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--auth':
        run_auth_flow()
    elif len(sys.argv) > 1 and sys.argv[1] == '--backup':
        backup_videos()
    else:
        print("""
============================================================
Google Drive Video Backup
============================================================

Usage:
  python3 backup_to_gdrive.py --auth      # Authorize Google Drive
  python3 backup_to_gdrive.py --backup    # Backup videos

First-time setup:
  1. Run: python3 backup_to_gdrive.py --auth
  2. Follow the browser authorization flow
  3. Then run: python3 backup_to_gdrive.py --backup
============================================================
""")
        if not os.path.exists(CRED_FILE):
            print("No credentials found. Starting authorization...")
            run_auth_flow()
        backup_videos()

if __name__ == "__main__":
    main()
