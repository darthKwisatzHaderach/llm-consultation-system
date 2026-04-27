from app.infra.celery_app import celery_app


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    return ""
