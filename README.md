# hacks_4easylife — daily auto-poster (zero-cost edition)

One hack per day, pulled from a pre-written bank → rendered as a branded card →
sent to your Telegram → you tap ✅ → it publishes to Instagram.
Runs on GitHub Actions. **No paid APIs. No AI tokens. Running cost: ₹0.**

## What costs nothing here
- **Content:** 66 pre-written hacks in `hacks.json` (~2 months). No AI call at run time.
- **Images:** rendered locally with Pillow on GitHub's free runners. No image API.
- **Hosting the image:** committed to your own repo, served via raw GitHub URL.
- **Scheduling / approval / posting:** GitHub Actions + Telegram + Instagram API — all free.

The only real work is the one-time credential setup below (~45 min).

---

## One-time setup

### 1. Put this in a GitHub repo
Create a repo (public or private both work — cards are served from a raw URL either way),
push these files.

### 2. Instagram / Meta credentials (`IG_USER_ID`, `IG_ACCESS_TOKEN`)
You already have: Creator account + linked Facebook Page in Business Suite. Now:
1. https://developers.facebook.com → create an app (type: **Business**).
2. Add the **Instagram Graph API** product.
3. App only serves your own account → **Standard Access, NO App Review needed.**
4. Generate a token with scopes: `instagram_basic`, `instagram_content_publish`,
   `pages_show_list`, `business_management`.
5. **Exchange it for a long-lived token** (short ones die in ~1 hour; long ~60 days).
6. Get `IG_USER_ID`: `GET /me/accounts` → your Page →
   `GET /{page-id}?fields=instagram_business_account`.

### 3. Telegram bot (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`)
1. Message **@BotFather** → `/newbot` → get token.
2. Message your new bot once.
3. Open `https://api.telegram.org/bot<TOKEN>/getUpdates` → find `"chat":{"id":...}`.

### 4. Add secrets to GitHub
Repo → Settings → Secrets and variables → Actions. Add exactly these **four**:
`IG_USER_ID`, `IG_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
(No Anthropic key — the AI step is gone.)

---

## Test before trusting
Repo → Actions → "Daily hack post" → **Run workflow**. Card should hit Telegram
in ~1 min. Tap ✅, check your IG grid.

## Daily behavior
Runs 09:30 IST (edit the cron in `.github/workflows/daily-post.yml`). Draft →
Telegram → tap ✅ to publish. No tap within 3 hours = auto-skip (nothing posts
unattended). The `state.json` counter advances each day so hacks never repeat
until the bank is used up.

## Refilling the bank (every ~2 months, free)
When `pick.py` logs "few left before repeat", open a normal Claude chat and ask
for a fresh batch of hacks in the same JSON format. Paste them into `hacks.json`,
push. Costs nothing — it's done in chat, not via API.

## Known limits (read these)
- **No text-only IG posts.** IG's feed API requires an image, so "text" days
  render a text-forward card; the caption carries the long text.
- **Token expiry is your #1 breakage.** The IG long-lived token lasts ~60 days.
  When posting suddenly fails, refresh it. Set a calendar reminder.
- **Automation ≠ growth.** This handles posting. Growth needs you to occasionally
  check which hacks get saved and reorder/refresh the bank toward what lands.

## Files
- `hacks.json` — the content bank (edit/extend this)
- `scripts/pick.py` — picks next hack, advances counter
- `scripts/make_card.py` — renders the two card layouts
- `scripts/render.py` — chooses layout by format
- `scripts/approve.py` — Telegram approve/skip
- `scripts/publish.py` — two-step IG publish with container polling
- `state.json` — auto-created counter (don't edit by hand)
