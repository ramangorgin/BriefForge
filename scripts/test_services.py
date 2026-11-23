#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")


def endpoint(base, path):
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def report(name, success, detail=""):
    print(f"[{'PASS' if success else 'FAIL'}] {name}")
    if detail:
        print(f"       {detail}")
    return success


def main():
    key = os.getenv("LLM_API_KEY", "").strip()
    base = os.getenv("LLM_BASE_URL", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()

    if not all((key, base, model)) or key == "replace_me":
        return 1 if not report(
            "Text model configuration",
            False,
            "Check LLM_API_KEY, LLM_BASE_URL and LLM_MODEL.",
        ) else 0

    try:
        response = requests.post(
            endpoint(base, "chat/completions"),
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Reply with exactly: BRIEFFORGE_OK"}],
                "temperature": 0,
                "max_tokens": 30,
            },
            timeout=int(os.getenv("LLM_TIMEOUT", "300")),
        )
        if not response.ok:
            detail = response.text[:600].replace("\n", " ")
            report("Text model API", False, f"HTTP {response.status_code}: {detail}")
            return 1

        answer = response.json()["choices"][0]["message"]["content"]
        report("Text model API", True, f"Model: {model}; response: {str(answer)[:150]}")
        return 0
    except Exception as exc:
        report("Text model API", False, str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
