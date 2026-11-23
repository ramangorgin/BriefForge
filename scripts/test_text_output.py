#!/usr/bin/env python3

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from brief_forge.config import settings
from brief_forge.llm import create_news_brief
from brief_forge.pipeline import format_news_brief, write_news_text


def check_model_api():
    if not settings.llm_api_key or settings.llm_api_key == "replace_me":
        return False, "LLM_API_KEY is missing or still set to replace_me"

    articles = [
        {
            "title": "Test AI model integration",
            "source": "BriefForge Test",
            "published": "2026-11-23",
            "summary": "A smoke-test article used to verify text model JSON output.",
            "url": "https://example.com/brief-forge-smoke-test",
        },
        {
            "title": "Test software development update",
            "source": "BriefForge Test",
            "published": "2026-11-23",
            "summary": "A second test story for validating article selection.",
            "url": "https://example.com/brief-forge-development",
        },
    ]

    try:
        plan = create_news_brief(articles, settings)
        news = plan.get("news")
        if not isinstance(news, list) or not news:
            return False, "The model did not return a non-empty news list"
        item = news[0]
        required = ("headline", "description", "highlights", "url")
        missing = [field for field in required if field not in item]
        if missing:
            return False, f"The model response is missing: {', '.join(missing)}"
        if not isinstance(item["highlights"], list):
            return False, "highlights must be a JSON list"
        return True, f"Model returned {len(news)} news item(s)"
    except Exception as exc:
        return False, str(exc)


def check_text_output():
    plan = {
        "edition_date": "2026-11-23",
        "language": "English",
        "news": [{
            "headline": "Test headline",
            "description": "A concise test description.",
            "highlights": ["First highlight", "Second highlight"],
            "source": "Example",
            "published": "2026-11-23",
            "url": "https://example.com/story",
        }],
    }

    text = format_news_brief(plan)
    for required in ("Test headline", "A concise test description.",
                     "First highlight", "Second highlight",
                     "https://example.com/story"):
        if required not in text:
            return False, f"Rendered text missing: {required}"

    with tempfile.TemporaryDirectory() as directory:
        path = write_news_text(plan, Path(directory) / "test.txt")
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            return False, "TXT file was not written correctly"

    return True, "TXT rendering and file writing passed"


def report(name, success, detail):
    print(f"[{'PASS' if success else 'FAIL'}] {name}")
    if detail:
        print(f"       {detail}")
    return success


def main():
    print("\nBriefForge text-output test")
    print("=" * 35)
    model_ok, model_detail = check_model_api()
    report("Text model API", model_ok, model_detail)
    text_ok, text_detail = check_text_output()
    report("TXT output", text_ok, text_detail)
    print("\nSummary")
    print("=" * 35)
    print(f"Passed: {sum((model_ok, text_ok))}/2")
    return 0 if model_ok and text_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
