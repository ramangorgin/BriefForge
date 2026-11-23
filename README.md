# BriefForge

BriefForge is a local-first Python application that collects technology news from RSS feeds and uses one OpenAI-compatible text model to select the strongest stories, write descriptions and highlights, and save a plain `.txt` briefing.

## Important limitations

- The first version uses RSS titles and feed summaries. It does **not** independently browse and verify every full article.
- The model is instructed not to invent facts, but generated content must still be checked against linked sources before presenting.
- Only one text-model API capability is required.

## Requirements

- Debian 13 and Python 3.13
- Internet access to your RSS sources and selected API providers
- An OpenAI-compatible LLM API key

## 1. Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Check versions:

```bash
python3 --version
```

## 2. Set up Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## 3. Configure API keys

```bash
cp .env.example .env
nano .env
```

Set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, and `NEWS_COUNT`.

The LLM endpoint must support OpenAI-compatible Chat Completions.

Never commit `.env` or share your API keys.

## 4. Configure RSS sources

Edit `config/feeds.txt`. Put one RSS URL per line; lines starting with `#` are ignored. Remove feeds that are unavailable or unreliable from your network.

## 5. Generate

```bash
source .venv/bin/activate
python -m brief_forge generate
```

The final `.txt` file is saved in `output/`.

## 6. Git

```bash
git init
git add .
git status
git commit -m "Initial BriefForge project"
```

The `.gitignore` excludes `.env`, generated files, virtual environments and `node_modules`.

## Configuration reference

| Variable | Purpose |
|---|---|
| `LLM_API_KEY` | Text-generation API key |
| `LLM_BASE_URL` | OpenAI-compatible text API base URL |
| `LLM_MODEL` | Chat model |
| `LANGUAGE` | Presentation language, e.g. Persian or English |
| `MAX_ARTICLES` | Maximum RSS items passed to the LLM |
| `NEWS_COUNT` | Number of selected news items to include |
| `DAYS_BACK` | RSS publication-age window |
| `OUTPUT_DIR` | Output directory |

## Workflow

1. Fetch RSS feeds.
2. Deduplicate URLs and filter old items where dates are available.
3. Ask the single text model to select stories and write JSON with descriptions and highlights.
4. Validate supplied URLs and render plain text.
5. Save the `.txt` briefing locally.

## Before using the news

- Open each source URL and verify names, dates, figures and technical claims.
- Replace or remove weak stories.
