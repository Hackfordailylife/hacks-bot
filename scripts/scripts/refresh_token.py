"""refresh_token.py — extends the IG long-lived token by another 60 days
and writes the new value to GITHUB_OUTPUT so the workflow can store it."""
import os, json, urllib.request, urllib.error

TOKEN = os.environ["IG_ACCESS_TOKEN"]
url = ("https://graph.instagram.com/refresh_access_token"
       f"?grant_type=ig_refresh_token&access_token={TOKEN}")

try:
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
except urllib.error.HTTPError as e:
    raise SystemExit(f"refresh failed ({e.code}): {e.read().decode(errors='replace')}")

new_token = data.get("access_token")
expires_in = data.get("expires_in")
if not new_token:
    raise SystemExit(f"no token in response: {data}")

print(f"refreshed OK, expires_in ~{int(expires_in)//86400} days")

with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"new_token={new_token}\n")
