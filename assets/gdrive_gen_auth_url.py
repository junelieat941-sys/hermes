#!/usr/bin/env python3
"""Generate Google Drive OAuth Authorization URL"""
import urllib.parse
import webbrowser
import sys

CLIENT_ID = "AIzaSyC9g28wpuJJ9HWfzmJIGS-X9O9xp6Etj-4"
REDIRECT_URI = "http://localhost:8085"
SCOPES = "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata"

# Generate auth URL
params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': SCOPES,
    'access_type': 'offline',
    'prompt': 'consent'
}
auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

print("="*70)
print("Google Drive OAuth Authorization")
print("="*70)
print()
print("STEP 1: Click the URL below to authorize")
print("-"*70)
print()
print(auth_url)
print()
print("-"*70)
print("STEP 2: Sign in to your Google account")
print("STEP 3: Click 'Allow' to grant permissions")
print("STEP 4: After authorization, you'll see an error page")
print("        (this is normal - redirect to localhost)")
print("STEP 5: Copy the 'code' parameter from the URL")
print("        Example: http://localhost:8085/?code=4/xxxx...")
print()
print("="*70)
print("STEP 6: Paste the authorization code below")
print("="*70)
print()

try:
    webbrowser.open(auth_url)
    print("✓ Browser opened automatically.")
except:
    print("Could not open browser. Please open the URL above manually.")
print()

# Get auth code
auth_code = input("Authorization code (paste after ?code=): ").strip()

if auth_code.startswith('code='):
    auth_code = auth_code[5:]
if auth_code.startswith('?code='):
    auth_code = auth_code[6:]

if not auth_code:
    print("\n✗ No authorization code provided")
    sys.exit(1)

print(f"\n✓ Received authorization code: {auth_code[:30]}...")
print("\nNext step: Exchange code for tokens")
print("Save this code and run the backup script, or provide it now:")
print()
print(f"  echo '{auth_code}' > /tmp/gdrive_auth_code")
print(f"  python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py --backup")
print()
print("Or run manually with the code:")
print(f"  export GDRIVE_AUTH_CODE='{auth_code}'")
print(f"  python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py --auth")
