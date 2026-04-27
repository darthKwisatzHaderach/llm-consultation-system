import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter


def _send_telegram_message(chat_id: int, text: str) -> None:
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


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    try:
        answer = call_openrouter(prompt)
    except Exception as exc:
        err = str(exc)
        if settings.telegram_bot_token:
            try:
                _send_telegram_message(tg_chat_id, f"Ошибка LLM: {err}")
            except Exception:
                pass
        return err
    if settings.telegram_bot_token:
        _send_telegram_message(tg_chat_id, answer)
    return answer
