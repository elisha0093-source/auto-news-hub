#!/usr/bin/env python3
import json, re, time, html, os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import feedparser

FEEDS = [
    {"url": "https://news.google.com/rss/search?q=%EC%9E%90%EB%8F%99%EC%B0%A8&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-자동차", "category": "domestic"},
    {"url": "https://news.google.com/rss/search?q=%EC%A0%84%EA%B8%B0%EC%B0%A8&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-전기차", "category": "domestic"},
    {"url": "https://news.google.com/rss/search?q=BYD%20%EC%A0%84%EA%B8%B0%EC%B0%A8&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-BYD", "category": "domestic"},
    {"url": "https://news.google.com/rss/search?q=%ED%98%84%EB%8C%80%EC%B0%A8%20%EA%B8%B0%EC%95%84&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-현대기아", "category": "domestic"},
    {"url": "https://news.google.com/rss/search?q=%EC%A0%9C%EB%84%A4%EC%8B%9C%EC%8A%A4%20%EC%8B%A0%EC%B0%A8&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-제네시스", "category": "domestic"},
    {"url": "https://news.google.com/rss/search?q=%EC%88%98%EC%9E%85%EC%B0%A8%20%EC%8B%A0%EC%B0%A8&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-수입차", "category": "domestic"},
    {"url": "https://electrek.co/feed/", "source": "Electrek", "category": "international"},
    {"url": "https://insideevs.com/rss/news/all/", "source": "InsideEVs", "category": "international"},
    {"url": "https://cnevpost.com/feed/", "source": "CnEVPost", "category": "international"},
    {"url": "https://cnevpost.com/byd/feed", "source": "CnEVPost-BYD", "category": "international", "force_byd": True},
    {"url": "https://www.motor1.com/rss/news/all/", "source": "Motor1", "category": "international"},
    {"url": "https://www.caranddriver.com/rss/news.xml", "source": "Car and Driver", "category": "international"},
    {"url": "https://www.teslarati.com/feed/", "source": "Teslarati", "category": "international"},
    {"url": "https://news.google.com/rss/search?q=%EA%B5%AD%ED%86%A0%EA%B5%90%ED%86%B5%EB%B6%80%20%EC%9E%90%EB%8F%99%EC%B0%A8&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-국토교통부", "category": "official"},
    {"url": "https://news.google.com/rss/search?q=%EC%9E%90%EB%8F%99%EC%B0%A8%20%EB%A6%AC%EC%BD%9C&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-리콜", "category": "official"},
    {"url": "https://news.google.com/rss/search?q=%EC%9E%90%EB%8F%99%EC%B0%A8%20%ED%8C%90%EB%A7%A4%EB%9F%89&hl=ko&gl=KR&ceid=KR:ko",
     "source": "구글뉴스-판매량통계", "category": "official"},
    {"url": "https://news.google.com/rss/search?q=NHTSA%20recall&hl=en-US&gl=US&ceid=US:en",
     "source": "구글뉴스-NHTSA", "category": "official"},
    {"url": "https://news.google.com/rss/search?q=IIHS%20crash%20test&hl=en-US&gl=US&ceid=US:en",
     "source": "구글뉴스-IIHS", "category": "official"},
    {"url": "https://news.google.com/rss/search?q=Euro%20NCAP&hl=en-US&gl=US&ceid=US:en",
     "source": "구글뉴스-EuroNCAP", "category": "official"},
]

MAX_ITEMS_PER_CATEGORY = 60
REQUEST_TIMEOUT = 15
BYD_EV_KEYWORDS = ["byd", "비야디", "전기차", "ev", "electric vehicle", "electric car",
    "배터리", "battery", "충전", "니오", "nio", "샤오미", "xpeng", "샤오펑",
    "테슬라", "tesla", "nev", "plug-in", "phev"]

def strip_html(raw_html):
    if not raw_html: return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()

def truncate(text, length=140):
    if len(text) <= length: return text
    return text[:length].rstrip() + "…"

def parse_date(entry):
    for key in ("published", "updated"):
        val = entry.get(key)
        if val:
            try:
                dt = parsedate_to_datetime(val)
                if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception: pass
    return datetime.now(timezone.utc)

def is_byd_ev(title, summary):
    blob = f"{title} {summary}".lower()
    return any(kw in blob for kw in BYD_EV_KEYWORDS)

def fetch_feed(feed_conf):
    url = feed_conf["url"]
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; AutoNewsHubBot/1.0)"})
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw = resp.read()
    except Exception as e:
        print(f"[WARN] fetch failed: {url} ({e})")
        return []
    parsed = feedparser.parse(raw)
    items = []
    for entry in parsed.entries:
        title = strip_html(entry.get("title", "")).strip()
        link = entry.get("link", "").strip()
        if not title or not link: continue
        summary_raw = entry.get("summary", "") or entry.get("description", "")
        summary = truncate(strip_html(summary_raw))
        published_dt = parse_date(entry)
        source_name = feed_conf["source"]
        m = re.match(r"^(.*)\s-\s([^-]+)$", title)
        if feed_conf["source"].startswith("구글뉴스") and m:
            title = m.group(1).strip()
            source_name = m.group(2).strip()
        domain = urlparse(link).netloc.replace("www.", "")
        items.append({
            "title": title, "link": link, "summary": summary,
            "source": source_name, "domain": domain,
            "category": feed_conf["category"],
            "published": published_dt.isoformat(),
            "published_ts": published_dt.timestamp(),
            "byd_ev": bool(feed_conf.get("force_byd")) or is_byd_ev(title, summary),
        })
    return items

def dedupe(items):
    seen, result = set(), []
    for it in items:
        if it["link"] in seen: continue
        seen.add(it["link"]); result.append(it)
    return result

def main():
    all_items = []
    for feed_conf in FEEDS:
        all_items.extend(fetch_feed(feed_conf))
        time.sleep(0.5)
    all_items = dedupe(all_items)
    all_items.sort(key=lambda x: x["published_ts"], reverse=True)

    domestic = [it for it in all_items if it["category"] == "domestic"][:MAX_ITEMS_PER_CATEGORY]
    international = [it for it in all_items if it["category"] == "international"][:MAX_ITEMS_PER_CATEGORY]
    official = [it for it in all_items if it["category"] == "official"][:MAX_ITEMS_PER_CATEGORY]
    byd_ev = [it for it in all_items if it["byd_ev"]][:MAX_ITEMS_PER_CATEGORY]

    for group in (domestic, international, official, byd_ev):
        for it in group: it.pop("published_ts", None)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {"domestic": len(domestic), "international": len(international), "official": len(official), "byd_ev": len(byd_ev)},
        "domestic": domestic, "international": international, "official": official, "byd_ev": byd_ev,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(domestic)} domestic / {len(international)} international / {len(official)} official / {len(byd_ev)} byd_ev items")

if __name__ == "__main__":
    main()
