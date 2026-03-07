"""
Run this script ONCE to get your OAuth2 refresh token.
Then paste the values into .env and delete this file.

Usage:
    .venv\Scripts\python.exe get_refresh_token.py
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

CLIENT_ID = input("Pega tu CLIENT_ID: ").strip()
CLIENT_SECRET = input("Pega tu CLIENT_SECRET: ").strip()

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

print("\n=== Copia estos valores en tu .env ===")
print(f"GOOGLE_CLIENT_ID={CLIENT_ID}")
print(f"GOOGLE_CLIENT_SECRET={CLIENT_SECRET}")
print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
