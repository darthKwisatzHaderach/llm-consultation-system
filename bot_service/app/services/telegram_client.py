import httpx

from app.core.config import settings


def send_telegram_message(chat_id: int, text: str) -> None:
    if not settings.telegram_bot_token:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                json={"chat_id": chat_id, "text": text},
            )
    except httpx.RequestError as exc:
        raise RuntimeError(f"Telegram: сеть — {exc}") from exc
    if response.status_code != 200:
        raise RuntimeError(
            f"Telegram: HTTP {response.status_code} — {(response.text or '')[:500]}"
        )
