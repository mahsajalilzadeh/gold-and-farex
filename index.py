from camoufox.sync_api import Camoufox
import time
import os
import requests



TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def get_chat_ids() -> set[int]:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    resp = requests.get(url, timeout=10)
    data = resp.json()

    chat_ids = set()

    for update in data.get("result", []):
        message = update.get("message")
        if message:
            chat_id = message["chat"]["id"]
            chat_ids.add(chat_id)

    return chat_ids

TGJU_URL = "https://www.tgju.org/profile/geram18"
CHECK_INTERVAL_SECONDS = 6 * 60 * 60  # 6 hours


def send_telegram_message(chat_id: int, text: str) -> None:
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
        print(f"Sent to {chat_id}")
    except Exception as exc:
        print(f"Failed to send to {chat_id}: {exc}")



# def send_telegram_message(text: str) -> None:
#     """Send a text message via Telegram Bot API to the configured chat id."""
#     if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
#         print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set.")
#         return

#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     try:
#         resp = requests.post(
#             url,
#             json={
#                 "chat_id": TELEGRAM_CHAT_ID,
#                 "text": text,
#                 "parse_mode": "HTML",
#             },
#             timeout=10,
#         )
#         data = resp.json()

#         if not data.get("ok"):
#             err = data.get("description", resp.text)
#             print(f"Telegram API error: {err}")
#             if "blocked" in str(err).lower() or "chat not found" in str(err).lower():
#                 print("راهنما: همسرتان باید اول با بات حرف بزنه — در تلگرام بات رو پیدا کنه و دکمه «شروع» (Start) رو بزنه.")
#             return

#         print("Message sent to Telegram.")
#     except requests.RequestException as exc:
#         print(f"Failed to send Telegram message (network): {exc}")
#     except ValueError as exc:
#         print(f"Invalid response from Telegram: {exc}")
#         print("Response text:", getattr(resp, "text", ""))


def fetch_gold_price() -> str | None:
    """Open tgju page with Camoufox and return the gold price text (or None on failure)."""
    with Camoufox() as browser:
        page = browser.new_page()
        page.goto(TGJU_URL)
        # Wait a bit for JS to load the price
        page.wait_for_timeout(6000)

        try:
            element = page.query_selector('[data-col="info.last_trade.PDrCotVal"]')

            if not element:
                print("Price element with class '.info-price' not found.")
                return None
            price_text = element.inner_text().strip()
            print(f"Fetched price: {price_text}")
            return price_text
        except Exception as exc:
            print(f"Error while fetching price: {exc}")
            return None





def main():
    price = fetch_gold_price()

    if price:
        message = f"قیمت فعلی طلای ۱۸ عیار: <b>{price}</b> ریال"

        chat_ids = get_chat_ids()

        for chat_id in chat_ids:
            send_telegram_message(chat_id, message)
    else:
        print("Price not fetched.")



# def main() -> None:
#     while True:
#         price = fetch_gold_price()

#         if price:
#             message = f"قیمت فعلی طلای ۱۸ عیار: <b>{price}</b> ریال"

#             chat_ids = get_chat_ids()

#             for chat_id in chat_ids:
#                 send_telegram_message(chat_id, message)

#         else:
#             print("Skipping Telegram send because price could not be fetched.")

#         time.sleep(5)


# def main() -> None:
#     while True:
#         price = fetch_gold_price()
#         if price:
#             message = f"قیمت فعلی طلای ۱۸ عیار: <b>{price}</b> ریال"
#             send_telegram_message(message)
#         else:
#             print("Skipping Telegram send because price could not be fetched.")

#         print(f"Sleeping for {CHECK_INTERVAL_SECONDS} seconds (6 hours)...")
#         try:
#             time.sleep(5)
#         except KeyboardInterrupt:
#             print("Stopped by user.")
#             break


if __name__ == "__main__":
    main()
