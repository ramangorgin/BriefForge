from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from html import unescape
import re
import feedparser

def load_feed_urls(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"RSS feed list not found: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]

def _published(entry):
    raw = entry.get("published") or entry.get("updated")
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except Exception:
        return None

def collect_articles(feed_urls, max_articles=35, days_back=7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    articles, seen, errors = [], set(), []
    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
            if parsed.bozo and not parsed.entries:
                errors.append(f"{url}: {parsed.bozo_exception}")
                continue
            source = parsed.feed.get("title", url)
            for entry in parsed.entries:
                link, title = entry.get("link", "").strip(), entry.get("title", "").strip()
                if not link or not title or link in seen:
                    continue
                published = _published(entry)
                if published is None:
                    continue
                if published < cutoff:
                    continue
                summary = entry.get("summary", "") or entry.get("description", "")
                summary = unescape(re.sub(r"<[^>]+>", " ", summary))
                summary = re.sub(r"\s+", " ", summary).strip()[:1800]
                articles.append({
                    "title": title[:400], "url": link, "source": source,
                    "published": published.isoformat(),
                    "summary": summary,
                    "_published": published,
                })
                seen.add(link)
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    articles.sort(key=lambda x: x["_published"], reverse=True)
    for article in articles:
        article.pop("_published", None)
    return articles[:max_articles], errors
