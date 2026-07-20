"""render.py — reads post.json, renders card.png with the right layout."""
import json
from make_card import make_card, make_text_card

post = json.load(open("post.json"))
if post["format"] == "text":
    make_text_card(post["category"], post["headline"], post["tip"], "card.png")
else:
    make_card(post["category"], post["headline"], post["tip"], "card.png")
print("rendered card.png")
