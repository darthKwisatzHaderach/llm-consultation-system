USAGE_TOKEN = "Использование: /token <jwt>"
PRIVATE_ONLY = "Команда доступна в личном чате с ботом."
TOKEN_BAD = "Токен недействителен или истёк. Получите новый в Auth Service."
TOKEN_SAVED = "Токен принят и сохранён."
UNKNOWN_COMMAND = "Неизвестная команда. Для привязки токена: /token <jwt>"


def no_token_registered(docs_url: str) -> str:
    return (
        "Нет сохранённого токена. Зарегистрируйтесь и возьмите JWT в Auth Service, "
        f"затем отправьте: /token <jwt>\nДокументация: {docs_url}"
    )


TOKEN_STALE = "Сохранённый токен недействителен. Отправьте новый: /token <jwt>"
REQUEST_ACCEPTED = "Запрос принят, ответ придёт в этом чате."
