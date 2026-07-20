"""
make_card.py — renders a 1080x1350 Instagram tip card for @hacks_4easylife
Save-optimized: bold headline, big legible tip, category tag, brand mark.
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ---- Brand palette: one consistent look per category so the grid stays cohesive ----
THEMES = {
    "money":    {"bg": "#0E3B43", "accent": "#F5B700", "text": "#FFFFFF"},
    "kitchen":  {"bg": "#7A2E1D", "accent": "#FFCF56", "text": "#FFF7ED"},
    "cleaning": {"bg": "#1B3A5B", "accent": "#5FD3C4", "text": "#F0FBFF"},
    "travel":   {"bg": "#2C1A47", "accent": "#FF7A9A", "text": "#FBF0FF"},
    "home":     {"bg": "#233329", "accent": "#B7E36A", "text": "#F3FCEB"},
}

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W, H = 1080, 1350
PAD = 90

def _font(path, size):
    return ImageFont.truetype(path, size)

def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def make_card(category, headline, tip, out_path="card.png"):
    t = THEMES.get(category, THEMES["money"])
    img = Image.new("RGB", (W, H), t["bg"])
    d = ImageDraw.Draw(img)

    # Top accent bar
    d.rectangle([0, 0, W, 16], fill=t["accent"])

    # Category tag
    tag_font = _font(BOLD, 34)
    tag = category.upper()
    d.text((PAD, 70), tag, font=tag_font, fill=t["accent"])

    # Headline (the hook)
    hl_font = _font(BOLD, 92)
    hl_lines = _wrap(d, headline, hl_font, W - 2*PAD)
    y = 150
    for ln in hl_lines:
        d.text((PAD, y), ln, font=hl_font, fill=t["text"])
        y += 104

    # Divider
    y += 30
    d.rectangle([PAD, y, PAD+120, y+8], fill=t["accent"])
    y += 60

    # Tip body
    body_font = _font(REG, 52)
    body_lines = _wrap(d, tip, body_font, W - 2*PAD)
    for ln in body_lines:
        d.text((PAD, y), ln, font=body_font, fill=t["text"])
        y += 72

    # Brand mark bottom
    brand_font = _font(BOLD, 40)
    brand = "@hacks_4easylife"
    bw = d.textlength(brand, font=brand_font)
    d.text(((W - bw)/2, H - 110), brand, font=brand_font, fill=t["accent"])

    # Save nudge
    sn_font = _font(REG, 30)
    sn = "\u2193 save this for later"
    sw = d.textlength(sn, font=sn_font)
    d.text(((W - sw)/2, H - 60), sn, font=sn_font, fill=t["text"])

    img.save(out_path, "PNG")
    return out_path

def make_text_card(category, headline, tip, out_path="card.png"):
    """Text-forward variant for 'text' days: big centered quote-style hack,
    no divider clutter. IG requires an image, so even 'text' posts get a card."""
    t = THEMES.get(category, THEMES["money"])
    img = Image.new("RGB", (W, H), t["bg"])
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 16], fill=t["accent"])

    quote_font = _font(BOLD, 76)
    lines = _wrap(d, headline, quote_font, W - 2*PAD)
    total_h = len(lines) * 88
    y = (H - total_h) // 2 - 120
    for ln in lines:
        lw = d.textlength(ln, font=quote_font)
        d.text(((W - lw)/2, y), ln, font=quote_font, fill=t["text"])
        y += 88

    y += 40
    sub_font = _font(REG, 44)
    for ln in _wrap(d, tip, sub_font, W - 2*PAD):
        lw = d.textlength(ln, font=sub_font)
        d.text(((W - lw)/2, y), ln, font=sub_font, fill=t["accent"])
        y += 60

    brand_font = _font(BOLD, 40)
    brand = "@hacks_4easylife"
    bw = d.textlength(brand, font=brand_font)
    d.text(((W - bw)/2, H - 90), brand, font=brand_font, fill=t["accent"])
    img.save(out_path, "PNG")
    return out_path

if __name__ == "__main__":
    make_card(
        "money",
        "Stop losing money to idle cash",
        "Move your emergency fund into a liquid mutual fund or high-yield savings account. Same access, but it earns 3-4x more than a regular savings account while you sleep.",
        "sample_card.png",
    )
    print("saved sample_card.png")
