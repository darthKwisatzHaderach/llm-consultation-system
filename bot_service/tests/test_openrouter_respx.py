import httpx
import respx

from app.services.openrouter_client import call_openrouter


@respx.mock
def test_openrouter_returns_message_content(respx_mock) -> None:
    route = respx_mock.post(
        "https://openrouter.ai/api/v1/chat/completions",
        name="openrouter-chat",
    ).mock(
        return_value=httpx.Response(
            status_code=200,
            json={"choices": [{"message": {"content": "ответ модели"}}]},
        ),
    )

    output = call_openrouter("prompt text")

    assert output == "ответ модели"
    assert route.called is True
