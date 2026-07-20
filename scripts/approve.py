"""
approve.py — sends the draft to Telegram with Approve/Reject buttons and
waits (polling getUpdates) for your tap. Exits 0 if approved, 1 if rejected/timeout.

Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
Reads: post.json  (and card.png if format == image)
"""
import os, json, time, urllib.request, urllib.parse

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT  = os.environ["TELEGRAM_CHAT_ID"]
API = f"https://api.telegram.org/bot{TOKEN}"
TIMEOUT_MIN = 180  # wait up to 3 hours for your tap, then auto-skip

def _post(method, **params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"{API}/{method}", data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def _send_photo(path, caption, markup):
    # multipart upload for the image
    boundary = "----hacksbot"
    with open(path, "rb") as f:
        img = f.read()
    parts = []
    def field(name, val):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n".encode())
    field("chat_id", CHAT)
    field("caption", caption[:1000])
    field("reply_markup", markup)
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"card.png\"\r\n"
        f"Content-Type: image/png\r\n\r\n".encode() + img + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        f"{API}/sendPhoto", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    post = json.load(open("post.json"))
    markup = json.dumps({"inline_keyboard": [[
        {"text": "\u2705 Post it", "callback_data": "approve"},
        {"text": "\u274c Skip",   "callback_data": "reject"},
    ]]})

    preview = f"*{post['headline']}*\n\n{post['tip']}\n\n\u2014\nCaption:\n{post['caption']}"

    if post["format"] == "image":
        _send_photo("card.png", preview, markup)
    else:
        _post("sendMessage", chat_id=CHAT, text=preview, parse_mode="Markdown",
              reply_markup=markup)

    # poll for the button tap
    deadline = time.time() + TIMEOUT_MIN * 60
    offset = None
    while time.time() < deadline:
        params = {"timeout": 30}
        if offset: params["offset"] = offset
        q = urllib.parse.urlencode(params)
        with urllib.request.urlopen(f"{API}/getUpdates?{q}", timeout=40) as r:
            updates = json.load(r).get("result", [])
        for u in updates:
            offset = u["update_id"] + 1
            cb = u.get("callback_query")
            if cb and str(cb["message"]["chat"]["id"]) == str(CHAT):
                decision = cb["data"]
                _post("answerCallbackQuery", callback_query_id=cb["id"],
                      text=("Publishing…" if decision == "approve" else "Skipped."))
                if decision == "approve":
                    print("APPROVED"); return 0
                else:
                    print("REJECTED"); raise SystemExit(1)
        time.sleep(2)
    print("TIMEOUT — no response, skipping"); raise SystemExit(1)

if __name__ == "__main__":
    raise SystemExit(main())
