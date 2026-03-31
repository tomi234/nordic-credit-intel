import feedparser
import json
import hashlib
import os
import time
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ─── LOGGING ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

# ─── CONFIG ─────────────────────────────────────────────────────────────────
GMAIL_USER         = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL    = os.environ.get("RECIPIENT_EMAIL", GMAIL_USER)
SCAN_INTERVAL_SEC  = int(os.environ.get("SCAN_INTERVAL_SEC", "900"))
SEEN_FILE          = "seen_items.json"

# ─── RSS FEEDS ───────────────────────────────────────────────────────────────
FEEDS = [
    "https://newsweb.oslobors.no/rss",
    "https://www.globenewswire.com/RssFeed/country/Norway",
    "https://www.globenewswire.com/RssFeed/country/Sweden",
    "https://www.globenewswire.com/RssFeed/country/Finland",
    "https://www.globenewswire.com/RssFeed/country/Denmark",
    "https://www.cisionwire.com/rss/all/",
]

# ─── KEYWORDS ────────────────────────────────────────────────────────────────
with open("keywords.json", "r", encoding="utf-8") as f:
    KW_CONFIG = json.load(f)

TRIGGER_KEYWORDS  = [k.lower() for k in KW_CONFIG.get("trigger_keywords", [])]
COMPANY_WATCHLIST = [c.lower() for c in KW_CONFIG.get("company_watchlist", [])]
EXCLUDE_KEYWORDS  = [k.lower() for k in KW_CONFIG.get("exclude_keywords", [])]

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def item_id(entry) -> str:
    raw = (entry.get("id") or entry.get("link") or entry.get("title") or "")
    return hashlib.md5(raw.encode()).hexdigest()

def matched_keywords(entry) -> list:
    text = (
        (entry.get("title") or "") + " " +
        (entry.get("summary") or "") + " " +
        (entry.get("description") or "")
    ).lower()

    for ex in EXCLUDE_KEYWORDS:
        if ex in text:
            return []

    matched = []
    for company in COMPANY_WATCHLIST:
        if company in text:
            matched.append(f"🏢 {company.title()}")
    for kw in TRIGGER_KEYWORDS:
        if kw in text:
            matched.append(f"🔑 {kw}")

    return matched

# ─── EMAIL ───────────────────────────────────────────────────────────────────
def build_html_email(entry, matches: list) -> str:
    title   = entry.get("title", "Ukjent tittel")
    summary = entry.get("summary") or entry.get("description") or "Ingen ingress tilgjengelig."
    link    = entry.get("link", "#")
    pub     = entry.get("published", "")
    source  = entry.get("source", {}).get("title", "") or link.split("/")[2] if link else ""
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Build match badges
    match_badges = ""
    seen_labels = set()
    for m in matches[:6]:
        if m not in seen_labels:
            seen_labels.add(m)
            color = "#f0c040" if "🏢" in m else "#4a9eff"
            match_badges += (
                f'<span style="display:inline-block;background:{color}22;'
                f'border:1px solid {color};color:{color};'
                f'font-size:11px;padding:2px 8px;border-radius:3px;'
                f'margin:2px 3px 2px 0;font-family:monospace;">{m}</span>'
            )

    # Prompt snippet for Claude
    prompt_text = (
        f"Tittel: {title}\\n\\n"
        f"Ingress: {summary}\\n\\n"
        f"Kilde: {link}"
    )

    return f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#0d0d1a;font-family:'Helvetica Neue',Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#0d0d1a;">
<tr><td align="center" style="padding:24px 12px;">
<table width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%;">

  <!-- Header -->
  <tr>
    <td style="background:linear-gradient(135deg,#1a1a3e 0%,#0d0d1a 100%);
               border-top:3px solid #f0c040;
               border-radius:8px 8px 0 0;
               padding:20px 28px 16px;">
      <p style="margin:0;font-size:10px;color:#6a7a9a;letter-spacing:3px;text-transform:uppercase;">
        📡 Nordic Credit Intel — Automatisk Skanning
      </p>
      <p style="margin:4px 0 0;font-size:11px;color:#4a5a7a;">
        {now_str} &nbsp;|&nbsp; Nytt treff funnet
      </p>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="background:#12122a;padding:28px;border-radius:0 0 8px 8px;
               border:1px solid #1e1e3e;border-top:none;">

      <!-- Match badges -->
      <div style="margin-bottom:16px;">
        {match_badges}
      </div>

      <!-- Title -->
      <h1 style="font-family:Georgia,serif;font-size:20px;color:#f0f4ff;
                 margin:0 0 12px;line-height:1.35;font-weight:normal;">
        {title}
      </h1>

      <!-- Meta -->
      <p style="margin:0 0 16px;font-size:11px;color:#4a5a7a;">
        {source} &nbsp;·&nbsp; {pub}
      </p>

      <hr style="border:none;border-top:1px solid #1e1e3e;margin:0 0 16px;">

      <!-- Summary -->
      <p style="font-size:14px;color:#c0cce0;line-height:1.6;margin:0 0 20px;">
        {summary}
      </p>

      <!-- Source link -->
      <p style="margin:0 0 24px;">
        <a href="{link}" style="display:inline-block;background:#1a1a3e;
           border:1px solid #f0c040;color:#f0c040;text-decoration:none;
           font-size:12px;padding:8px 16px;border-radius:4px;letter-spacing:0.5px;">
          📰 Les full artikkel →
        </a>
      </p>

      <hr style="border:none;border-top:1px solid #1e1e3e;margin:0 0 20px;">

      <!-- CTA -->
      <div style="background:#0a0a1e;border:1px solid #2a2a4a;border-radius:6px;padding:18px;">
        <p style="margin:0 0 8px;font-size:12px;color:#f0c040;
                  letter-spacing:1px;text-transform:uppercase;font-weight:bold;">
          💬 Analyser med Claude AI (gratis)
        </p>
        <p style="margin:0 0 12px;font-size:13px;color:#8a9ab8;line-height:1.5;">
          Kopier teksten under og lim den inn i Claude.ai for å få full credit flash-analyse:
        </p>
        <div style="background:#06060f;border:1px solid #1e1e3e;border-radius:4px;
                    padding:14px;font-family:monospace;font-size:12px;
                    color:#a0b4c8;line-height:1.6;word-break:break-word;">
          Analyser denne nyheten som credit analyst:<br><br>
          Tittel: {title}<br><br>
          Ingress: {summary[:300]}{"..." if len(summary) > 300 else ""}<br><br>
          Kilde: {link}
        </div>
      </div>

      <br>
      <p style="margin:0;font-size:10px;color:#2a3a5a;line-height:1.6;">
        Dette er ikke investeringsrådgivning. For profesjonelle investorer.<br>
        Nordic Credit Intel · Nordea Markets Securities Advisory · Oslo
      </p>

    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

def send_email(subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
    log.info(f"✉️  Sendt: {subject}")

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────
def scan_once(seen: set) -> set:
    new_seen = set(seen)
    found = 0

    for feed_url in FEEDS:
        try:
            log.info(f"Skanner: {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                eid = item_id(entry)
                if eid in seen:
                    continue
                new_seen.add(eid)

                matches = matched_keywords(entry)
                if not matches:
                    continue

                title = entry.get("title", "Ukjent")
                log.info(f"🎯 TREFF: {title}")
                log.info(f"   Matcher: {matches[:3]}")

                try:
                    html    = build_html_email(entry, matches)
                    subject = f"📡 Credit: {title[:65]}"
                    send_email(subject, html)
                    found += 1
                    time.sleep(1)
                except Exception as e:
                    log.error(f"Feil ved sending: {e}")

        except Exception as e:
            log.error(f"Feil ved skanning av {feed_url}: {e}")

    if found == 0:
        log.info("Ingen nye relevante nyheter denne runden.")
    else:
        log.info(f"✅ Sendte {found} credit flash(er)")

    return new_seen

def main():
    log.info("🚀 Nordic Credit Intel (gratis versjon) startet")
    log.info(f"📋 Følger {len(COMPANY_WATCHLIST)} selskaper | {len(TRIGGER_KEYWORDS)} triggere")
    log.info(f"📬 Sender til: {RECIPIENT_EMAIL}")
    log.info(f"⏱️  Skanner hvert {SCAN_INTERVAL_SEC // 60}. minutt")

    seen = load_seen()

    while True:
        try:
            seen = scan_once(seen)
            save_seen(seen)
        except Exception as e:
            log.error(f"Kritisk feil: {e}")
        log.info(f"💤 Neste skanning om {SCAN_INTERVAL_SEC // 60} min...")
        time.sleep(SCAN_INTERVAL_SEC)

if __name__ == "__main__":
    main()
