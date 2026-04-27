import httpx

from app.core.config import settings


def call_openrouter(user_prompt: str) -> str:
    if not settings.openrouter_api_key:
        raise RuntimeError("OpenRouter: не задан OPENROUTER_API_KEY")

    base = settings.openrouter_base_url.rstrip("/")
    url = f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=body, headers=headers)
    except httpx.RequestError as exc:
        raise RuntimeError(f"OpenRouter: сеть недоступна — {exc}") from exc

    if response.status_code != 200:
        text = (response.text or "")[:800]
        raise RuntimeError(
            f"OpenRouter: HTTP {response.status_code} — {text}"
        )

    data = response.json()
    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        snippet = repr(data)[:400]
        raise RuntimeError(f"OpenRouter: неожиданный JSON ответ: {snippet}") from exc
