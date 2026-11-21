
#!/usr/bin/env python3

import base64
import os
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

TIMEOUT = 120


def env(name, default=""):
    return os.getenv(name, default).strip()


def endpoint(base, path):
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def report(name, success, detail=""):
    print(f"[{'PASS' if success else 'FAIL'}] {name}")
    if detail:
        print(f"       {detail}")
    return success


def error_message(response):
    try:
        data = response.json()
        error = data.get("error", data)
        if isinstance(error, dict):
            error = error.get("message", error)
        return str(error)[:600]
    except Exception:
        return response.text[:600].replace("\n", " ")


def test_llm():
    key = env("LLM_API_KEY")
    base = env("LLM_BASE_URL")
    model = env("LLM_MODEL")

    if not all((key, base, model)):
        return report("LLM configuration", False, "Check LLM_API_KEY, LLM_BASE_URL and LLM_MODEL.")

    try:
        response = requests.post(
            endpoint(base, "chat/completions"),
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": "Reply with exactly: BRIEFFORGE_OK"}
                ],
                "temperature": 0,
                "max_tokens": 30,
            },
            timeout=TIMEOUT,
        )

        if not response.ok:
            return report("LLM API", False, f"HTTP {response.status_code}: {error_message(response)}")

        answer = response.json()["choices"][0]["message"]["content"]
        return report("LLM API", True, f"Model: {model}; response: {str(answer)[:150]}")

    except Exception as exc:
        return report("LLM API", False, str(exc))


def test_image():
    key = env("IMAGE_API_KEY")
    base = env("IMAGE_BASE_URL")
    model = env("IMAGE_MODEL")
    size = env("IMAGE_SIZE", "1536x1024")

    if not all((key, base, model)):
        return report("Image configuration", False, "Check IMAGE_API_KEY, IMAGE_BASE_URL and IMAGE_MODEL.")

    try:
        response = requests.post(
            endpoint(base, "images/generations"),
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "prompt": (
                    "Professional editorial illustration for a computer science "
                    "news presentation. Abstract connected computer chips, "
                    "modern technology magazine style, no text."
                ),
                "size": size,
                "n": 1,
                "response_format": "b64_json",
            },
            timeout=TIMEOUT,
        )

        if not response.ok:
            return report("Image API", False, f"HTTP {response.status_code}: {error_message(response)}")

        item = response.json()["data"][0]
        workspace = ROOT / env("WORKSPACE_DIR", "workspace")
        workspace.mkdir(parents=True, exist_ok=True)
        image_path = workspace / "api_test_image.png"

        if item.get("b64_json"):
            image_bytes = base64.b64decode(item["b64_json"])
        elif item.get("url"):
            image_response = requests.get(item["url"], timeout=TIMEOUT)
            image_response.raise_for_status()
            image_bytes = image_response.content
        else:
            return report("Image API", False, "No image data or URL in the response.")

        if not (
            image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
            or image_bytes.startswith(b"\xff\xd8")
        ):
            return report("Image API", False, "Response is not a PNG/JPEG image.")

        image_path.write_bytes(image_bytes)
        return report("Image API", True, f"Saved image: {image_path.relative_to(ROOT)}")

    except Exception as exc:
        return report("Image API", False, str(exc))


def test_powerpoint():
    output_dir = ROOT / env("OUTPUT_DIR", "output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "brief_forge_smoke_test.pptx"

    js = r"""
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "BriefForge";
pptx.subject = "PowerPoint smoke test";
pptx.title = "BriefForge Test";

const slide = pptx.addSlide();
slide.background = { color: "101827" };

slide.addText("BriefForge", {
    x: 0.7, y: 1.6, w: 12, h: 0.8,
    fontSize: 34, bold: true,
    color: "FFFFFF", align: "center"
});

slide.addText("PowerPoint generation is working.", {
    x: 1, y: 2.6, w: 11.3, h: 0.6,
    fontSize: 20, color: "B9C7D8",
    align: "center"
});

slide.addNotes(
    "BRIEFFORGE TEST SPEAKER NOTES\n\n" +
    "If you can read this in Presenter View, " +
    "speaker notes were successfully added."
);

pptx.writeFile({ fileName: process.argv[1] })
    .then(() => process.exit(0))
    .catch(err => {
        console.error(err);
        process.exit(1);
    });
"""

    try:
        result = subprocess.run(
            ["node", "-e", js, str(output_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return report(
                "PowerPoint generation",
                False,
                (result.stderr or result.stdout)[:600],
            )

        if not output_path.exists() or output_path.stat().st_size < 1000:
            return report("PowerPoint generation", False, "PPTX file missing or invalid.")

        return report(
            "PowerPoint generation",
            True,
            f"Created {output_path.relative_to(ROOT)} ({output_path.stat().st_size:,} bytes)",
        )

    except FileNotFoundError:
        return report("PowerPoint generation", False, "Node.js not found.")
    except Exception as exc:
        return report("PowerPoint generation", False, str(exc))


def main():
    print("\nBriefForge diagnostics")
    print("=" * 35)

    results = [
        test_llm(),
        test_image(),
        test_powerpoint(),
    ]

    print("\nSummary")
    print("=" * 35)
    print(f"Passed: {sum(results)}/{len(results)}")

    if not all(results):
        print("Some tests failed. Check the error messages above.")
        return 1

    print("All diagnostic tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
