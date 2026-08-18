"""render.py — reads post.json (a carousel), renders one PNG per slide."""
import json
from make_card import make_card

post = json.load(open("post.json"))
category = post["category"]
slides = post["slides"]

if not (2 <= len(slides) <= 10):
    raise SystemExit(f"carousel needs 2-10 slides, got {len(slides)}")

for i, s in enumerate(slides):
    out = f"slide_{i}.png"
    make_card(category, s["headline"], s["body"], out)
    print(f"rendered {out}")

print(f"rendered {len(slides)} slides")
