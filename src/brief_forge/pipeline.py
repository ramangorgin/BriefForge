from datetime import datetime
from pathlib import Path
import json
import subprocess
from .config import PROJECT_ROOT
from .feeds import load_feed_urls, collect_articles
from .llm import create_editorial_plan
from .images import generate_slide_image

def run_generation(settings):
    settings.validate()
    feeds = load_feed_urls(settings.feeds_file)
    print(f"[1/5] Collecting RSS articles from {len(feeds)} feeds...")
    articles, errors = collect_articles(feeds, settings.max_articles, settings.days_back)
    if len(articles) < 3:
        details = "\n".join(errors[:5])
        raise RuntimeError(
            f"Only {len(articles)} usable articles were collected. Check network/RSS feeds.\n{details}"
        )
    print(f"      Collected {len(articles)} articles.")
    if errors:
        print(f"      Warning: {len(errors)} feed(s) could not be read.")

    print("[2/5] Asking the LLM to select stories and write the presentation...")
    plan = create_editorial_plan(articles, settings)
    slides = plan["slides"]

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    work_dir = settings.workspace_dir / run_id
    image_dir = work_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[3/5] Generating {len(slides)} slide illustrations...")
    for index, slide in enumerate(slides, start=1):
        target = image_dir / f"slide_{index:02d}.png"
        print(f"      Image {index}/{len(slides)}: {slide.get('title', 'Untitled')}")
        generate_slide_image(slide, index, settings, target)
        slide["image_path"] = str(target.resolve())

    manifest = work_dir / "manifest.json"
    manifest.write_text(json.dumps({
        "title": plan.get("presentation_title", settings.presentation_title),
        "edition_date": plan.get("edition_date", ""),
        "language": settings.language,
        "slides": slides
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[4/5] Building PowerPoint with private speaker notes...")
    node_script = PROJECT_ROOT / "deck" / "build_deck.js"
    if not (PROJECT_ROOT / "node_modules" / "pptxgenjs").exists():
        raise RuntimeError("PptxGenJS is not installed. Run: npm install")
    output_path = settings.output_dir / f"BriefForge_{run_id}.pptx"
    subprocess.run(["node", str(node_script), str(manifest), str(output_path)], check=True)

    print("[5/5] Finished.")
    print(f"Presentation: {output_path.resolve()}")
    print("Reminder: RSS summaries are leads, not independent verification.")
    return output_path
