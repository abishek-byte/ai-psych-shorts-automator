"""Standalone YouTube token generator - no imports needed."""
import json
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import google.oauth2.credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Load client secrets from file
with open("client_secrets.json", "r") as f:
    client_secrets = json.load(f)

flow = InstalledAppFlow.from_client_config(client_secrets, SCOPES)
creds = flow.run_local_server(port=0)

print("\n" + "="*60)
print("COPY THIS ENTIRE JSON TO GITHUB SECRET 'YOUTUBE_TOKEN':")
print("="*60)
print(creds.to_json())
print("="*60)