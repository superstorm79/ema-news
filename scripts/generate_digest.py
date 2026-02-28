#!/usr/bin/env python3
"""
החדשות של אמה — Daily Digest Generator
Calls Claude API to generate a Hebrew news digest for a 10-year-old,
publishes it as an HTML file, and notifies via WhatsApp.
"""

import os
import json
import datetime
import requests
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CALLMEBOT_PHONE   = os.environ["CALLMEBOT_PHONE"]    # e.g. 972501234567
CALLMEBOT_APIKEY  = os.environ["CALLMEBOT_APIKEY"]   # from callmebot.com
GITHUB_REPO_NAME  = os.environ["GITHUB_REPOSITORY"]  # e.g. yourname/ema-news
PAGES_BASE_URL    = os.environ["PAGES_BASE_URL"]      # e.g. https://yourname.github.io/ema-news

OUTPUT_DIR = Path("docs")  # GitHub Pages serves from /docs

# ── PROMPT ───────────────────────────────────────────────────────────────────

def build_prompt(date_str: str, day_name: str) -> str:
    return f"""אתה עורך של עיתון ילדים יומי בעברית בשם "החדשות של אמה".
הקוראת היא ילדה בת 10 חיה בישראל, סקרנית, חכמה, ואוהבת לדעת מה קורה בעולם.
התאריך היום הוא {day_name}, {date_str}.

## עקרונות העריכה
1. **קרא לדברים בשמם** — אם משהו קשה קורה, אמור זאת במשפט אחד ברור.
2. **פנה לתגובה האנושית** — אחרי שמת את הקושי, תמיד ענה: מה אנשים עושים בנוגע לזה?
3. **אין מספרי הרוגים או פצועים** — לעולם. ניתן לציין שיש עימות; לא את הפרטים הדמיים.
4. **אי-וודאות היא כנה** — "אנחנו עדיין לא יודעים כיצד זה יסתיים" הוא משפט שלם ומכובד.
5. **חיים רגילים קיימים לצד דברים קשים** — אם שני הדברים אמיתיים, אמור שניהם.
6. **היא הקוראת, לא המוגנת** — כתוב כאילו היא חכמה, סקרנית ומסוגלת לשבת עם מורכבות.

## מבנה הגיליון
צור בדיוק את הסעיפים הבאים בסדר הזה:

### 1. 🇮🇱 קרוב לבית (Israel)
כתבה אחת על ישראל. עדיפות: חדשות שמשפיעות על חיי היומיום, פוליטיקה מקומית, הישגים ישראליים, אירועי תרבות/ספורט. אם המצב הביטחוני רלוונטי — ציין אותו בכנות אבל ללא גרפיקה.

### 2. 🌍 מבט על העולם (World)
2-3 כתבות על אירועים גלובליים חשובים. כלול עימותים ופוליטיקה אם הם עיקר החדשות — אבל תמיד עם מסגרת של "מה אנשים עושים בנוגע לזה".

### 3. 🔬 גילוי היום (Science/Nature)
1-2 כתבות מדע, חלל, טבע, בעלי חיים, ארכאולוגיה. זה הסעיף הכי קל — מדע טוב הוא תמיד מרגש.

### 4. 💡 זרקור טכנולוגי (Tech)
כתבה אחת על טכנולוגיה — ממוקדת במה שהיא *עושה לאנשים*, לא רק מה היא.

### 5. 🎨 פינת תרבות (Culture)
כתבה אחת — ספר, סרט, אמן, אירוע תרבותי, המצאה יצירתית. גשר בין תרבות פופ למציאות.

### 6. 💬 מילה ותהייה
- **מילה של היום**: מילה אחת מהכתבות של היום עם הגדרה פשוטה ומעניינת
- **שאלה לשיחת ערב**: שאלה פתוחה אחת שמזמינה שיחה משפחתית עמוקה

## כלי עיצוב לתוכן
בתוך כל כתבה, השתמש בדיוק בשתי תיבות אלה כשרלוונטי:
- `[HONEST]טקסט[/HONEST]` — עובדה מרכזית כנה, מה שחשוב להבין
- `[OPENQ]טקסט[/OPENQ]` — מה שעדיין לא ידוע

## פורמט הפלט
החזר JSON בלבד, ללא שום טקסט נוסף לפניו או אחריו. המבנה:

{{
  "sections": [
    {{
      "id": "israel",
      "icon": "🇮🇱",
      "label": "קרוב לבית",
      "color": "#e8f4f0",
      "stories": [
        {{
          "tag": "תווית קצרה",
          "tag_type": "israel",
          "headline": "כותרת הכתבה",
          "body": "טקסט הכתבה עם [HONEST]...[/HONEST] ו-[OPENQ]...[/OPENQ] כשרלוונטי"
        }}
      ]
    }},
    {{
      "id": "world",
      "icon": "🌍", 
      "label": "מבט על העולם",
      "color": "#e8f4e8",
      "stories": [...]
    }},
    {{
      "id": "science",
      "icon": "🔬",
      "label": "גילוי היום", 
      "color": "#e8eef8",
      "stories": [...]
    }},
    {{
      "id": "tech",
      "icon": "💡",
      "label": "זרקור טכנולוגי",
      "color": "#f5f0e8",
      "stories": [...]
    }},
    {{
      "id": "culture",
      "icon": "🎨",
      "label": "פינת תרבות",
      "color": "#f8e8f0",
      "stories": [...]
    }}
  ],
  "word_of_day": {{
    "word": "המילה",
    "definition": "הגדרה פשוטה ומעניינת"
  }},
  "think_question": "השאלה לשיחת ערב"
}}

חפש חדשות אמיתיות של היום. כתוב בעברית טבעית ועשירה המתאימה לילדה בת 10 חכמה."""


# ── HTML RENDERER ─────────────────────────────────────────────────────────────

def render_story_body(body: str) -> str:
    """Convert [HONEST]...[/HONEST] and [OPENQ]...[/OPENQ] to HTML."""
    import re
    body = re.sub(
        r'\[HONEST\](.*?)\[/HONEST\]',
        r'<div class="honest-line">\1</div>',
        body, flags=re.DOTALL
    )
    body = re.sub(
        r'\[OPENQ\](.*?)\[/OPENQ\]',
        r'<div class="open-q">\1</div>',
        body, flags=re.DOTALL
    )
    return body


def render_html(data: dict, date_str: str, day_name: str) -> str:
    sections_html = ""
    for i, section in enumerate(data["sections"]):
        stories_html = ""
        for story in section["stories"]:
            tag_type = story.get("tag_type", "world")
            body = render_story_body(story["body"])
            stories_html += f"""
      <div class="story">
        <span class="tag tag-{tag_type}">{story['tag']}</span>
        <div class="story-headline">{story['headline']}</div>
        <div class="story-body">{body}</div>
        <div class="rating">
          <span class="rating-label">דרגי</span>
          <span class="star" onclick="rate(this)">★</span>
          <span class="star" onclick="rate(this)">★</span>
          <span class="star" onclick="rate(this)">★</span>
          <span class="star" onclick="rate(this)">★</span>
          <span class="star" onclick="rate(this)">★</span>
        </div>
      </div>"""

        sections_html += f"""
  <div class="section s-{section['id']}" style="--section-color:{section['color']}">
    <div class="section-header">
      <span class="section-icon">{section['icon']}</span>
      <span class="section-label">{section['label']}</span>
    </div>
    <div class="section-body">{stories_html}
    </div>
  </div>"""

    word = data["word_of_day"]
    think = data["think_question"]

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>החדשות של אמה – {date_str}</title>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;700;900&family=Heebo:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --cream:#fdf6ec; --ink:#1a1208; --warm-mid:#7a5c3a;
    --accent:#e8612c; --accent-light:#fde8dc; --rule:#d4c4aa;
    --honest-bg:#f7f3ee; --honest-border:#c4a882;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--cream); color:var(--ink); font-family:'Heebo',sans-serif; font-size:15px; line-height:1.85; direction:rtl; }}

  .masthead {{ border-bottom:3px double var(--ink); padding:22px 40px 20px; text-align:center; background:var(--cream); }}
  .masthead-date {{ font-family:'Frank Ruhl Libre',serif; font-size:20px; font-weight:700; color:var(--ink); margin-bottom:4px; }}
  .masthead-meta {{ display:flex; justify-content:space-between; font-size:11px; color:var(--warm-mid); font-weight:500; margin-bottom:14px; }}
  .masthead h1 {{ font-family:'Frank Ruhl Libre',serif; font-size:clamp(46px,9vw,82px); font-weight:900; line-height:1.05; color:var(--ink); }}
  .masthead h1 span {{ color:var(--accent); }}
  .masthead-sub {{ font-family:'Frank Ruhl Libre',serif; font-size:16px; color:var(--warm-mid); margin-top:8px; }}
  .rule-thin {{ border:none; border-top:1px solid var(--rule); margin:12px auto; width:80%; }}

  .container {{ max-width:820px; margin:0 auto; padding:0 24px 60px; }}

  .section {{ margin:28px 0; border-radius:4px; overflow:hidden; border:1px solid var(--rule); animation:fadeUp 0.5s ease both; }}
  .section:nth-child(1){{animation-delay:0.05s}} .section:nth-child(2){{animation-delay:0.12s}}
  .section:nth-child(3){{animation-delay:0.19s}} .section:nth-child(4){{animation-delay:0.26s}}
  .section:nth-child(5){{animation-delay:0.33s}} .section:nth-child(6){{animation-delay:0.40s}}
  @keyframes fadeUp {{ from{{opacity:0;transform:translateY(14px)}} to{{opacity:1;transform:translateY(0)}} }}

  .section-header {{ padding:14px 22px; display:flex; align-items:center; gap:14px; border-bottom:2px solid var(--rule); background:var(--section-color); }}
  .section-icon {{ font-size:28px; line-height:1; flex-shrink:0; }}
  .section-label {{ font-family:'Frank Ruhl Libre',serif; font-size:24px; font-weight:900; color:var(--ink); }}
  .section-body {{ padding:20px 24px; background:white; }}

  .story {{ padding:18px 0; border-bottom:1px solid #f0e8dc; }}
  .story:last-child {{ border-bottom:none; padding-bottom:4px; }}
  .story-headline {{ font-family:'Frank Ruhl Libre',serif; font-size:18px; font-weight:700; line-height:1.4; color:var(--ink); margin-bottom:10px; }}
  .story-body {{ font-size:14.5px; line-height:1.9; color:#3a2e22; font-weight:300; }}
  .story-body strong {{ font-weight:600; color:var(--ink); }}

  .honest-line {{ margin:12px 0 4px; padding:10px 14px; background:var(--honest-bg); border-right:3px solid var(--honest-border); border-radius:0 3px 3px 0; font-size:13.5px; color:#4a3a28; line-height:1.7; font-style:italic; }}
  .honest-line::before {{ content:"מה שאנחנו יודעים: "; font-style:normal; font-weight:700; color:var(--warm-mid); font-size:12px; }}
  .open-q {{ margin-top:10px; font-size:13px; color:#7a6a58; font-style:italic; }}
  .open-q::before {{ content:"עדיין לא ידוע: "; font-style:normal; font-weight:700; font-size:12px; color:var(--accent); }}

  .word-box {{ background:var(--ink); color:var(--cream); border-radius:4px; padding:20px 24px; margin-bottom:20px; }}
  .word-box .label {{ font-size:11px; color:var(--accent); font-weight:600; margin-bottom:6px; }}
  .word-box .word {{ font-family:'Frank Ruhl Libre',serif; font-size:30px; font-weight:900; margin-bottom:8px; color:white; }}
  .word-box .definition {{ font-size:13.5px; color:#c8b89a; line-height:1.7; font-weight:300; }}

  .think-box {{ background:var(--accent-light); border-right:3px solid var(--accent); padding:16px 20px; border-radius:0 4px 4px 0; }}
  .think-box .label {{ font-size:11px; font-weight:700; color:var(--accent); margin-bottom:8px; }}
  .think-box p {{ font-family:'Frank Ruhl Libre',serif; font-size:17px; line-height:1.6; color:var(--ink); }}

  .footer {{ text-align:center; padding:28px; border-top:3px double var(--ink); font-size:12px; color:var(--warm-mid); font-weight:500; margin-top:20px; }}

  .rating {{ margin-top:12px; display:flex; gap:4px; align-items:center; flex-direction:row-reverse; justify-content:flex-end; }}
  .rating-label {{ font-size:11px; color:#9a8878; margin-left:6px; font-weight:500; }}
  .star {{ cursor:pointer; font-size:20px; color:#d4c4aa; transition:color 0.15s,transform 0.1s; user-select:none; }}
  .star:hover,.star.active {{ color:#e8a020; transform:scale(1.2); }}

  .tag {{ display:inline-block; font-size:10px; font-weight:700; padding:3px 10px; border-radius:2px; margin-bottom:10px; }}
  .tag-world   {{ background:#d4eed4; color:#2d6b2d; }}
  .tag-science {{ background:#d4e4f4; color:#1e4d7a; }}
  .tag-tech    {{ background:#ede4d4; color:#6b4d1e; }}
  .tag-israel  {{ background:#d4f4e8; color:#1e6b4d; }}
  .tag-complex {{ background:#ede0d4; color:#7a3a1a; }}
  .tag-culture {{ background:#f4d4e8; color:#6b1e4d; }}

  @media(max-width:580px) {{
    .masthead{{padding:18px 16px 16px}} .masthead-meta{{flex-direction:column;gap:2px;text-align:center}}
    .container{{padding:0 12px 40px}} .section-body{{padding:14px 16px}} .section-label{{font-size:20px}}
  }}
</style>
</head>
<body>

<div class="masthead">
  <div class="masthead-date">{day_name}, {date_str}</div>
  <hr class="rule-thin">
  <h1>החדשות <span>של אמה</span></h1>
  <div class="masthead-sub">כל החדשות שחשוב לדעת — רק בשבילך</div>
  <hr class="rule-thin">
  <div class="masthead-meta"><span>מהדורה אישית</span><span>גיליון יומי</span></div>
</div>

<div class="container">
{sections_html}

  <div class="section" style="border-color:var(--rule)">
    <div class="section-header" style="background:#f5f0e8">
      <span class="section-icon">💬</span>
      <span class="section-label">מילה ותהייה</span>
    </div>
    <div class="section-body">
      <div class="word-box">
        <div class="label">מילה של היום</div>
        <div class="word">{word['word']}</div>
        <div class="definition">{word['definition']}</div>
      </div>
      <div class="think-box">
        <div class="label">משהו לחשוב עליו — לשיחת ערב</div>
        <p>{think}</p>
      </div>
    </div>
  </div>
</div>

<div class="footer">
  החדשות של אמה · {day_name}, {date_str} · נעשה באהבה ❤️ רק בשבילך
</div>

<script>
  function rate(star) {{
    const stars = star.parentElement.querySelectorAll('.star');
    const idx = Array.from(stars).indexOf(star);
    stars.forEach((s,i) => {{ if(i<=idx) s.classList.add('active'); else s.classList.remove('active'); }});
  }}
</script>
</body>
</html>"""


# ── CLAUDE API CALL ───────────────────────────────────────────────────────────

def call_claude(prompt: str) -> dict:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-opus-4-6",
            "max_tokens": 4000,
            "tools": [{"type": "web_search_20250305", "name": "web_search"}],
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=120
    )
    response.raise_for_status()
    result = response.json()

    # Extract text content from response (may include tool_use blocks)
    text = ""
    for block in result.get("content", []):
        if block.get("type") == "text":
            text += block["text"]

    # Strip any markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)


# ── WHATSAPP NOTIFICATION ─────────────────────────────────────────────────────

def send_whatsapp(page_url: str, date_str: str, headlines: list[str]):
    preview = " · ".join(headlines[:3])
    message = (
        f"📰 *החדשות של אמה מוכנות!*\n"
        f"{date_str}\n\n"
        f"היום: {preview}\n\n"
        f"🔗 {page_url}\n\n"
        f"_בדקי לפני שתעבירי לה_ ✅"
    )
    encoded = requests.utils.quote(message)
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={CALLMEBOT_PHONE}&text={encoded}&apikey={CALLMEBOT_APIKEY}"
    )
    r = requests.get(url, timeout=30)
    print(f"WhatsApp status: {r.status_code}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # Date setup (Israel timezone)
    import zoneinfo
    tz = zoneinfo.ZoneInfo("Asia/Jerusalem")
    today = datetime.datetime.now(tz).date()

    day_names = {
        0: "יום שני", 1: "יום שלישי", 2: "יום רביעי",
        3: "יום חמישי", 4: "יום שישי", 5: "שבת", 6: "יום ראשון"
    }
    day_name = day_names[today.weekday()]
    date_str = f"{today.day} ב{['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'][today.month-1]} {today.year}"
    slug = today.strftime("%Y-%m-%d")

    print(f"Generating digest for {date_str}...")

    # Generate content
    prompt = build_prompt(date_str, day_name)
    data = call_claude(prompt)

    # Render HTML
    html = render_html(data, date_str, day_name)

    # Save to docs/ (GitHub Pages)
    output_path = OUTPUT_DIR / f"{slug}.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    # Also write as index.html so the root URL shows today's digest
    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")

    print(f"Saved: {output_path}")

    # Build page URL
    page_url = f"{PAGES_BASE_URL}/{slug}.html"

    # Collect headlines for WhatsApp preview
    headlines = []
    for section in data["sections"]:
        for story in section["stories"]:
            headlines.append(story["headline"])

    # Send WhatsApp
    send_whatsapp(page_url, date_str, headlines)
    print("Done!")


if __name__ == "__main__":
    main()
