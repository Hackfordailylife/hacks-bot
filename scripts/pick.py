"""
pick.py — zero-cost replacement for the old AI generator.
Reads hacks.json, picks the next entry in order using a counter file committed
to the repo, writes post.json. No API, no tokens, no cost.

When the bank is exhausted it wraps around to the start (so it never breaks),
but you'll want to top it up before then \u2014 see README.
"""
import json, os

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {"index": 0}

def main():
    hacks = json.load(open("hacks.json"))
    state = load_state()
    i = state["index"] % len(hacks)

    post = hacks[i]
    with open("post.json", "w") as f:
        json.dump(post, f, indent=2)

    # advance and persist (workflow commits state.json so it carries to tomorrow)
    state["index"] = (state["index"] + 1) % len(hacks)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    remaining = len(hacks) - (i + 1)
    print(json.dumps(post, indent=2))
    print(f"\n[pick] used #{i+1}/{len(hacks)} \u2014 {remaining} left before repeat")

if __name__ == "__main__":
    main()
