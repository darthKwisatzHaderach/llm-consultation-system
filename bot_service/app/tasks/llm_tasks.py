from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter
from app.services.telegram_client import send_telegram_message


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    try:
        answer = call_openrouter(prompt)
    except Exception as exc:
        err = str(exc)
        if settings.telegram_bot_token:
            try:
                send_telegram_message(tg_chat_id, f"Ошибка LLM: {err}")
            except Exception:
                pass
        return err
    if settings.telegram_bot_token:
        send_telegram_message(tg_chat_id, answer)
    return answer
