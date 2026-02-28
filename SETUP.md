# 🗞️ החדשות של אמה — Setup Guide
**One-time setup. Takes about 30 minutes.**

---

## What you'll end up with
Every morning at 7:00am Israel time, Claude searches today's news, writes Ema's digest in Hebrew, publishes it to a webpage, and sends you a WhatsApp message with the link to review before forwarding to her.

---

## Step 1 — Create a GitHub account (if you don't have one)
1. Go to [github.com](https://github.com) and sign up (free)
2. Choose any username — e.g. `ema-news-parent`

---

## Step 2 — Create the repository
1. Click the **+** button (top right) → **New repository**
2. Name it: `ema-news`
3. Set it to **Public** *(required for free GitHub Pages hosting)*
4. Tick **"Add a README file"**
5. Click **Create repository**

---

## Step 3 — Upload the project files
In your new repository:
1. Click **Add file** → **Upload files**
2. Upload everything from this package:
   - `scripts/generate_digest.py` → upload into a `scripts/` folder
   - `.github/workflows/daily_digest.yml` → upload into `.github/workflows/`
3. Create a `docs/` folder by uploading any placeholder file into it
   (e.g. a file called `docs/.gitkeep` with empty contents)
4. Commit the changes

---

## Step 4 — Enable GitHub Pages
1. In your repository, go to **Settings** → **Pages** (left sidebar)
2. Under **Source**, select: **Deploy from a branch**
3. Branch: `main` | Folder: `/docs`
4. Click **Save**
5. After a minute, GitHub will show you your site URL:
   `https://YOUR-USERNAME.github.io/ema-news`
   **Copy this URL — you'll need it in Step 6.**

---

## Step 5 — Get your Anthropic API key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / log in
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)
5. Add a small credit balance (credit card required) — the digest costs roughly **$0.10–0.20/day** (~50–100₪/month)

---

## Step 6 — Set up WhatsApp notifications (CallMeBot)
This is the free service that sends WhatsApp messages automatically.

1. Save this number in your contacts: **+34 644 69 67 42** (CallMeBot)
2. Send this message to that number on WhatsApp:
   `I allow callmebot to send me messages`
3. You'll receive a reply with your personal **API key** (a string of numbers)
4. Your phone number for the config should be in international format without `+`:
   e.g. if your number is `+972 50 123 4567`, use `972501234567`

---

## Step 7 — Add your secrets to GitHub
Your API keys should never be in code files. GitHub stores them safely.

1. In your repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add each of these:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic key from Step 5 |
| `CALLMEBOT_PHONE` | Your phone number (e.g. `972501234567`) |
| `CALLMEBOT_APIKEY` | The key CallMeBot sent you in Step 6 |
| `PAGES_BASE_URL` | Your GitHub Pages URL from Step 4 (e.g. `https://yourname.github.io/ema-news`) |

---

## Step 8 — Test it manually
Before waiting for the morning, trigger it manually to make sure everything works:

1. In your repository, go to **Actions** (top menu)
2. Click **Generate Daily Digest — החדשות של אמה**
3. Click **Run workflow** → **Run workflow**
4. Watch the logs — it should take about 60–90 seconds
5. If it succeeds: check your WhatsApp for the notification, and visit your GitHub Pages URL

---

## Step 9 — Share the page with Ema
Once it's running, her daily link will always be:
```
https://YOUR-USERNAME.github.io/ema-news
```
That URL always shows today's digest (it updates every morning).

You can also bookmark the dated version each day:
```
https://YOUR-USERNAME.github.io/ema-news/2026-02-28.html
```

---

## Timing
The digest runs at **04:00 UTC** which is:
- **07:00 Israel time** in summer (March–October, UTC+3) ✓
- **06:00 Israel time** in winter (October–March, UTC+2)

If you want 07:00 in winter too, change the cron line in the workflow file to:
```
- cron: '0 5 * * *'
```
during winter months. Or just leave it — 06:00 is still early enough for review before school.

---

## Daily routine
Every morning you'll receive a WhatsApp from yourself (via CallMeBot) that looks like:

> 📰 *החדשות של אמה מוכנות!*
> 28 בפברואר 2026
>
> היום: ארה״ב ואיראן שוב מדברות · דינוזאור חדש בסהרה · מרתון תל אביב
>
> 🔗 https://yourname.github.io/ema-news/2026-02-28.html
>
> *בדקי לפני שתעבירי לה* ✅

Open the link, glance through it (2 min), then forward it to Ema's WhatsApp.

---

## Troubleshooting

**The workflow failed** → Go to Actions → click the failed run → read the error log. Most common issues:
- Wrong API key (check secrets spelling exactly)
- Anthropic account has no credit balance

**No WhatsApp received** → Make sure you sent the activation message to CallMeBot first (Step 6). Sometimes it takes a few minutes.

**The page looks wrong** → The JSON from Claude was malformed. Run it again manually — this is rare.

**Need to change the editorial rules?** → Edit the `build_prompt()` function in `scripts/generate_digest.py`. All the filtering logic lives there.

---

## Monthly cost estimate
| Service | Cost |
|---|---|
| GitHub (hosting + automation) | Free |
| CallMeBot (WhatsApp) | Free |
| Anthropic API | ~$3–6/month |
| **Total** | **~$3–6/month** |

---

*Built with love for Ema 💙*
