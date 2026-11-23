from datetime import datetime
from pathlib import Path
from .feeds import load_feed_urls, collect_articles
from .llm import create_news_brief


def format_news_brief(plan):
    lines = [
        "Technology News Brief",
        f"Date: {plan.get('edition_date', '')}",
        f"Language: {plan.get('language', '')}",
        "",
    ]
    news = plan.get("news", [])
    for index, item in enumerate(news, start=1):
        lines.extend([
            f"{index}. {item['headline']}",
            f"Description: {item['description']}",
            "Highlights:",
        ])
        for highlight in item.get("highlights", []):
            lines.append(f"- {highlight}")
        lines.extend([
            f"Source: {item.get('source', '')}",
            f"Published: {item.get('published', '')}",
            f"Link: {item['url']}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_news_text(plan, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_news_brief(plan), encoding="utf-8")
    return output_path

def run_generation(settings):
    settings.validate()
    feeds = load_feed_urls(settings.feeds_file)
    print(f"[1/3] Collecting RSS articles from {len(feeds)} feeds...")
    articles, errors = collect_articles(feeds, settings.max_articles, settings.days_back)
    if len(articles) < 1:
        details = "\n".join(errors[:5])
        raise RuntimeError(
            f"No usable articles were collected. Check network/RSS feeds.\n{details}"
        )
    if len(articles) < settings.news_count:
        raise RuntimeError(
            f"Only {len(articles)} articles are available within "
            f"DAYS_BACK={settings.days_back}, but NEWS_COUNT={settings.news_count}."
        )
    print(f"      Collected {len(articles)} articles.")
    if errors:
        print(f"      Warning: {len(errors)} feed(s) could not be read.")

    print("[2/3] Asking the text model to select stories and write highlights...")
    plan = create_news_brief(articles, settings)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = settings.output_dir / f"BriefForge_{run_id}.txt"
    write_news_text(plan, output_path)

    print("[3/3] Finished.")
    print(f"News file: {output_path.resolve()}")
    print("Reminder: RSS summaries are leads, not independent verification.")
    return output_path
