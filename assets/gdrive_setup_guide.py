#!/usr/bin/env python3
"""Simple Google Drive OAuth2 Authorization"""
import os
import json
import http.server
import socketserver
import threading
import webbrowser
import urllib.parse
import urllib.request
import sys

STATE_FILE = os.path.expanduser("~/.gdrive_state.json")
CRED_FILE = os.path.expanduser("~/.gdrive_credentials.json")

# In a real scenario, you'd need:
# 1. Google Cloud Project with Drive API enabled
# 2. OAuth 2.0 Desktop client credentials
# For demo/development, we can use the "quickstart" approach

print("""
============================================================
Google Drive Backup Setup
============================================================

To backup videos to Google Drive, you need OAuth credentials:

STEP 1: Create Google Cloud Project
1. Go to: https://console.cloud.google.com/
2. Create new project (or select existing)
3. Name it something like "Hermes Backup"

STEP 2: Enable Google Drive API
1. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com
2. Click "Enable"

STEP 3: Create OAuth Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Hermes Backup"
5. Click "CREATE"
6. Download the JSON file (click the download icon)

STEP 4: Save Credentials
1. Rename downloaded file to: client_secret.json
2. Save to: ~/.gdrive_client_secret.json
   (i.e., /home/codespace/.gdrive_client_secret.json)

STEP 5: Run Authorization
1. Run this command:
   python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py --auth

You'll be asked to:
- Open a URL in your browser
- Sign in to Google
- Grant permission
- Copy the authorization code back
""")

# Check if client secret exists
client_secret_path = os.path.expanduser("~/.gdrive_client_secret.json")
if os.path.exists(client_secret_path):
    print(f"\nFound client secret at: {client_secret_path}")
    with open(client_secret_path) as f:
        secret = json.load(f)
        client_id = secret.get('installed', {}).get('client_id', '')
        if client_id:
            print(f"Client ID: {client_id[:30]}...")
            print("\nNow run: python3 /workspaces/hermes-agent/assets/backup_to_gdrive.py --auth")
        else:
            print("\nError: Invalid client secret format")
else:
    print(f"\nClient secret not found at: {client_secret_path}")
    print("\nPlease complete the steps above first.")
