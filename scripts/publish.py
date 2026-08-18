"""publish.py — publishes the approved post to Instagram via graph.instagram.com."""
import os, json, time, urllib.request, urllib.parse, urllib.error

IG_USER = os.environ["IG_USER_ID"]
TOKEN   = os.environ["IG_ACCESS_TOKEN"]
GRAPH   = "https://graph.instagram.com/v21.0"

def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GET failed ({e.code}): {e.read().decode(errors='replace')}")

def _post(path, params):
    data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"{GRAPH}/{path}", data=data, method="POST"), timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"POST {path} failed ({e.code}): {e.read().decode(errors='replace')}")

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

def publish(cid, tries=3):
    for attempt in range(1, tries + 1):
        try:
            res = _post(f"{IG_USER}/media_publish",
                        {"creation_id": cid, "access_token": TOKEN})
            if "id" in res:
                return res
            raise RuntimeError(f"publish failed: {res}")
        except RuntimeError as e:
            # 9007 = media not ready; retry after a short wait
            if "9007" in str(e) and attempt < tries:
                print(f"publish not ready (attempt {attempt}), retrying in 10s...")
                time.sleep(10)
                continue
            raise
    raise RuntimeError("publish failed after retries")

def main():
    post = json.load(open("post.json"))
    cid = create_container(post)
    wait_finished(cid)
    time.sleep(2)  # settle buffer after FINISHED before publishing
    res = publish(cid)
    print(f"PUBLISHED media id {res['id']}")

if __name__ == "__main__":
    main()
