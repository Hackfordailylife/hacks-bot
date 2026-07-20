"""
publish.py — publishes the approved post to Instagram.

For image posts: the card.png is committed to the repo by the workflow BEFORE
this runs, so it's reachable at a raw.githubusercontent.com URL (a public URL
the IG API can pull — no third-party image host needed).

Two-step flow with the container-processing wait that Meta's docs bury:
  1) POST /{ig_user_id}/media            -> container id
  2) poll GET /{container_id}?fields=status_code until FINISHED
  3) POST /{ig_user_id}/media_publish    -> live post

Env: IG_USER_ID, IG_ACCESS_TOKEN (long-lived), and for image posts IMAGE_URL
"""
import os, json, time, urllib.request, urllib.parse, urllib.error

IG_USER = os.environ["IG_USER_ID"]
TOKEN   = os.environ["IG_ACCESS_TOKEN"]
GRAPH   = "https://graph.instagram.com/v21.0"

def _read(resp):
    return json.load(resp)

def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return _read(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"GET failed ({e.code}): {body}")

def _post(path, params):
    data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"{GRAPH}/{path}", data=data, method="POST"), timeout=60) as r:
            return _read(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"POST {path} failed ({e.code}): {body}")

def create_container(post):
    params = {"caption": post["caption"], "access_token": TOKEN}
    params["image_url"] = os.environ["IMAGE_URL"]
    res = _post(f"{IG_USER}/media", params)
    if "id" not in res:
        raise RuntimeError(f"container failed: {res}")
    return res["id"]

def wait_finished(container_id, tries=20):
    for _ in range(tries):
        q = urllib.parse.urlencode({"fields": "status_code", "access_token": TOKEN})
        res = _get(f"{GRAPH}/{container_id}?{q}")
        status = res.get("status_code")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"container errored: {res}")
        time.sleep(5)
    raise TimeoutError("container never reached FINISHED")

def main():
    post = json.load(open("post.json"))
    cid =
