"""publish.py — publishes an approved CAROUSEL post to Instagram via graph.instagram.com.

Flow:
  1. create one item container per slide image  (is_carousel_item=true)
  2. create the parent carousel container       (media_type=CAROUSEL, children=...)
  3. poll the parent until FINISHED
  4. publish the parent

Expects:
  - env IG_USER_ID, IG_ACCESS_TOKEN
  - env SLIDE_URLS  -> comma-separated public image URLs (2-10), in slide order
  - post.json       -> the selected carousel object; only 'caption' is read here
"""
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


def create_item_container(image_url, tries=3):
    """One child container per slide. Retries in case the raw URL 404s briefly."""
    last = None
    for attempt in range(1, tries + 1):
        res = _post(f"{IG_USER}/media", {
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": TOKEN,
        })
        if "id" in res:
            return res["id"]
        last = res
        time.sleep(5)
    raise RuntimeError(f"item container failed for {image_url}: {last}")


def create_carousel_container(child_ids, caption):
    res = _post(f"{IG_USER}/media", {
        "media_type": "CAROUSEL",
        "children": ",".join(child_ids),
        "caption": caption,
        "access_token": TOKEN,
    })
    if "id" not in res:
        raise RuntimeError(f"carousel container failed: {res}")
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
            if "9007" in str(e) and attempt < tries:
                print(f"publish not ready (attempt {attempt}), retrying in 10s...")
                time.sleep(10)
                continue
            raise
    raise RuntimeError("publish failed after retries")


def main():
    post = json.load(open("post.json"))
    caption = post["caption"]

    slide_urls = [u.strip() for u in os.environ["SLIDE_URLS"].split(",") if u.strip()]
    if not (2 <= len(slide_urls) <= 10):
        raise RuntimeError(f"carousel needs 2-10 slides, got {len(slide_urls)}")

    child_ids = [create_item_container(u) for u in slide_urls]
    print(f"created {len(child_ids)} item containers")

    parent_id = create_carousel_container(child_ids, caption)
    print(f"created carousel container {parent_id}")

    wait_finished(parent_id)
    time.sleep(2)
    res = publish(parent_id)
    print(f"PUBLISHED carousel media id {res['id']}")


if __name__ == "__main__":
    main()
