# BriefForge

BriefForge is a local-first Python application that collects technology news from RSS feeds, asks an OpenAI-compatible LLM to create an editorial presentation plan, generates one consistent visual per slide, and builds a PowerPoint (`.pptx`) file with private speaker notes.

## Important limitations

- The first version uses RSS titles and feed summaries. It does **not** independently browse and verify every full article.
- The model is instructed not to invent facts, but generated content must still be checked against linked sources before presenting.
- Text and image generation are separate API capabilities. Providers must expose compatible endpoints.
- The image adapter expects an OpenAI-compatible Images API response containing either `b64_json` or `url`.
- PptxGenJS generates the PPTX because native speaker notes are required. LibreOffice Impress can open the resulting PPTX.

## Requirements

- Debian 13, Python 3.13, Node.js and npm
- Internet access to your RSS sources and selected API providers
- An LLM API key and an image-generation API key (possibly the same key)

## 1. Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm
```

Check versions:

```bash
python3 --version
node --version
npm --version
```

## 2. Set up Python and Node dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
npm install
```

## 3. Configure API keys

```bash
cp .env.example .env
nano .env
```

Set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `IMAGE_API_KEY`, `IMAGE_BASE_URL` and `IMAGE_MODEL`.

The LLM endpoint must support OpenAI-compatible Chat Completions. The image endpoint must support the OpenAI-compatible Images API used by the OpenAI Python SDK. Not every provider supports both; check its documentation before configuring it.

Never commit `.env` or share your API keys.

## 4. Configure RSS sources

Edit `config/feeds.txt`. Put one RSS URL per line; lines starting with `#` are ignored. Remove feeds that are unavailable or unreliable from your network.

## 5. Generate

```bash
source .venv/bin/activate
python -m brief_forge generate
```

The final `.pptx` is saved in `output/`.

## 6. Git

```bash
git init
git add .
git status
git commit -m "Initial BriefForge project"
```

The `.gitignore` excludes `.env`, generated files, workspace data, virtual environments and `node_modules`.

## Configuration reference

| Variable | Purpose |
|---|---|
| `LLM_API_KEY` | Text-generation API key |
| `LLM_BASE_URL` | OpenAI-compatible text API base URL |
| `LLM_MODEL` | Chat model |
| `IMAGE_API_KEY` | Image-generation API key |
| `IMAGE_BASE_URL` | Image API base URL |
| `IMAGE_MODEL` | Image model |
| `IMAGE_SIZE` | Image dimensions accepted by provider |
| `LANGUAGE` | Presentation language, e.g. Persian or English |
| `MAX_ARTICLES` | Maximum RSS items passed to the LLM |
| `MAX_SLIDES` | Maximum requested slide count |
| `DAYS_BACK` | RSS publication-age window |
| `OUTPUT_DIR` | Output directory |
| `WORKSPACE_DIR` | Intermediate plans and images |

## Workflow

1. Fetch RSS feeds.
2. Deduplicate URLs and filter old items where dates are available.
3. Ask the LLM to select stories and write a JSON slide plan.
4. Generate one image per slide using a fixed visual style prompt.
5. Build a widescreen PPTX with editable titles and private speaker notes.
6. Save the presentation locally.

## Before presenting

- Open each source URL and verify names, dates, figures and technical claims.
- Replace or remove weak stories.
- Check Persian font rendering and right-to-left text in LibreOffice.
- Rehearse and time the narration.
- Test that speaker notes appear in Impress and on your Android remote.
# BriefForge
