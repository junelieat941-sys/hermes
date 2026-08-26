#!/usr/bin/env python3
"""Google Drive OAuth2 Authorization Flow"""
import os
import json
import http.server
import socketserver
import threading
import webbrowser
import urllib.parse
import sys

# Google OAuth2 settings
CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8085"
SCOPES = "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata"

STATE_FILE = os.path.expanduser("~/.gdrive_state.json")
CRED_FILE = os.path.expanduser("~/.gdrive_credentials.json")

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    success = None
    error = None
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if 'code' in params:
            OAuthHandler.success = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html><body>
                    <h3>Authorization successful!</h3>
                    <p>You can close this window and return to the terminal.</p>
                </body></html>
            ''')
        elif 'error' in params:
            OAuthHandler.error = params['error'][0]
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {params['error'][0]}".encode())
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

def run_oauth_server():
    with socketserver.TCPServer(("localhost", 8085), OAuthHandler) as httpd:
        httpd.serve_forever()

def get_oauth_url():
    """Generate OAuth URL"""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for tokens"""
    import urllib.request
    
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }).encode()
    
    req = urllib.request.Request(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as response:
        tokens = json.loads(response.read().decode())
        return tokens

def main():
    print("=" * 60)
    print("Google Drive OAuth2 Authorization")
    print("=" * 60)
    
    # Check if we have credentials
    if os.path.exists(CRED_FILE):
        print("\nFound existing credentials. Skipping authorization.")
        return
    
    if CLIENT_ID == "YOUR_CLIENT_ID.apps.googleusercontent.com":
        print("\nError: Please set up Google OAuth credentials first:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create project and enable Google Drive API")
        print("3. Create OAuth 2.0 Desktop credentials")
        print("4. Update CLIENT_ID and CLIENT_SECRET in this script")
        return
    
    # Start OAuth server in background
    server_thread = threading.Thread(target=run_oauth_server, daemon=True)
    server_thread.start()
    
    # Get OAuth URL
    auth_url = get_oauth_url()
    
    print("\nPlease visit this URL to authorize:")
    print(auth_url)
    print("\nOr pressing Enter will try to open it automatically...")
    
    input()
    webbrowser.open(auth_url)
    
    print("\nWaiting for authorization callback...")
    print("(Check your browser for the Google authorization page)")
    
    # Wait for authorization
    import time
    for i in range(60):  # Wait up to 60 seconds
        if OAuthHandler.success:
            auth_code = OAuthHandler.success
            break
        if OAuthHandler.error:
            print(f"\nAuthorization error: {OAuthHandler.error}")
            sys.exit(1)
        time.sleep(1)
    else:
        print("\nTimeout waiting for authorization")
        sys.exit(1)
    
    print("\nExchanging code for tokens...")
    tokens = exchange_code_for_tokens(auth_code)
    
    # Save credentials
    creds = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tokens.get("refresh_token"),
        "access_token": tokens.get("access_token"),
        "token_expiry": tokens.get("expires_in")
    }
    
    with open(CRED_FILE, "w") as f:
        json.dump(creds, f, indent=2)
    
    print(f"\nCredentials saved to {CRED_FILE}")
    print("\nYou can now use Google Drive backup!")
    print("Run: python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py")

if __name__ == "__main__":
    main()
