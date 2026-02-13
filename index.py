import os
import requests
from bs4 import BeautifulSoup


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TGJU_URL = "https://www.tgju.org/profile/geram18"


def get_chat_ids() -> set[int]:
    """Read chat_ids that have interacted with the bot via getUpdates."""
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set.")
        return set()

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"Failed to call getUpdates: {exc}")
        return set()

    chat_ids: set[int] = set()

    for update in data.get("result", []):
        message = update.get("message")
        if message:
            chat_id = message["chat"]["id"]
            chat_ids.add(chat_id)

    return chat_ids


def send_telegram_message(chat_id: int, text: str) -> None:
    """Send message to a single chat_id via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        resp = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        data = resp.json()
        if not data.get("ok"):
            print(f"Telegram API error for {chat_id}: {data.get('description', resp.text)}")
            return

        print(f"Sent to {chat_id}")
    except Exception as exc:
        print(f"Failed to send to {chat_id}: {exc}")


def fetch_gold_price() -> str | None:
    """Fetch tgju page via HTTP and extract the gold price."""
    try:
        resp = requests.get(TGJU_URL, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        print(f"HTTP error while fetching page: {exc}")
        return None

    try:
        soup = BeautifulSoup(resp.text, "html.parser")

        # اول با کلاس info-price که خودت در Inspect دیدی
        el = soup.select_one('[data-col="info.last_trade.PDrCotVal"]')

        # # اگر پیدا نشد، سِلکتور بک‌آپ
        # if not el:
        #     el = soup.select_one('[data-col="info.last_trade.PDrCotVal"]')

        if not el:
            print("Price element not found in HTML.")
            return None

        price_text = el.get_text(strip=True)
        print(f"Fetched price: {price_text}")
        return price_text
    except Exception as exc:
        print(f"Error while parsing HTML: {exc}")
        return None


def main() -> None:
    price = fetch_gold_price()

    if not price:
        print("Price not fetched.")
        return

    message = f"قیمت فعلی طلای ۱۸ عیار: <b>{price}</b> ریال"

    chat_ids = get_chat_ids()
    if not chat_ids:
        print("No chat_ids found in getUpdates. Make sure you and your wife have started the bot in Telegram.")
        return

    for chat_id in chat_ids:
        send_telegram_message(chat_id, message)


if __name__ == "__main__":
    main()