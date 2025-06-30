# MOEX News Parser

This repository contains a simple parser that retrieves news from [nsddata.ru](https://nsddata.ru/ru/news) and posts updates to a Telegram channel.

The parser filters news items by keywords `DVCA`, `INTR` and `REDM` and publishes matching events.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create two environment variables with your Telegram credentials:

- `TELEGRAM_BOT_TOKEN` – token of your Telegram bot.
- `TELEGRAM_CHAT_ID` – identifier of the chat or channel where messages will be sent.


3. Run the parser:

```bash
python scripts/parse_nsd_news.py
```

To change the keywords, pass them with `--keyword`:

```bash
python scripts/parse_nsd_news.py --keyword dvca --keyword intr
```

The script remembers the last processed news ID in `news_state.json` to avoid sending duplicates.

## Quick test

To confirm that the Telegram token is available in the environment run:

```bash
python - <<'PY'
import os
print("TOKEN_PRESENT", bool(os.getenv("TELEGRAM_BOT_TOKEN")))
PY
```
