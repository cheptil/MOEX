"""Fetch and post NSD news to Telegram."""

import os
import json
import re
from pathlib import Path
from typing import Iterable, List, Tuple

import requests
from bs4 import BeautifulSoup

URL = "https://nsddata.ru/ru/news"
STATE_FILE = Path(__file__).with_name("news_state.json")
DEFAULT_KEYWORDS = ["dvca", "intr", "redm"]


def fetch_page() -> str:
    """Return the HTML of the NSD news page."""
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(URL, timeout=30, headers=headers)
    resp.raise_for_status()
    return resp.text


def parse_news(html: str, keywords: Iterable[str]) -> List[Tuple[int, str, str, str]]:
    """Parse news items matching *keywords* from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".news_list__item")
    news: List[Tuple[int, str, str, str]] = []
    for item in items:
        date_div = item.select_one(".news_list__item__date")
        title_link = item.select_one(".news_list__item__header__title")
        if not date_div or not title_link:
            continue
        date = date_div.get_text(strip=True)
        text = title_link.get_text(strip=True)
        link = "https://nsddata.ru" + title_link["href"]
        match = re.search(r"/view/(\d+)", title_link["href"])
        news_id = int(match.group(1)) if match else 0
        if any(k.lower() in text.lower() for k in keywords):
            news.append((news_id, date, text, link))
    return news


def load_state() -> int:
    """Return the last processed news ID or ``0`` if none is stored."""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("last_id", 0))
    except FileNotFoundError:
        return 0


def save_state(last_id: int) -> None:
    """Persist the last processed news ID."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_id": last_id}, f)


def send_telegram(text: str) -> None:
    """Send *text* to the configured Telegram chat."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("Telegram credentials are not set")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, data=payload, timeout=30)
    resp.raise_for_status()


def main(keywords: Iterable[str] = DEFAULT_KEYWORDS) -> None:
    """Fetch and publish NSD news matching *keywords*."""
    html = fetch_page()
    news = parse_news(html, keywords)
    if not news:
        return
    last_id = load_state()
    new_last_id = last_id
    for news_id, date, text, link in sorted(news, key=lambda x: x[0]):
        if news_id > last_id:
            message = f"{date} - {text}\n{link}"
            send_telegram(message)
            if news_id > new_last_id:
                new_last_id = news_id
    if new_last_id != last_id:
        save_state(new_last_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Post NSD news to Telegram")
    parser.add_argument(
        "-k",
        "--keyword",
        dest="keywords",
        action="append",
        help="keyword to filter news (can be repeated)",
    )
    args = parser.parse_args()

    keywords = args.keywords if args.keywords else DEFAULT_KEYWORDS
    main(keywords)
