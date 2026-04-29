from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot.redis_keys import jwt_storage_key
from app.core.config import settings
from app.core.jwt import is_valid_token
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


def _auth_swagger_url() -> str:
    return f"{settings.auth_service_url.rstrip('/')}/docs"


@router.message(Command("token"))
async def token_cmd(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        await message.answer("Команда доступна в личном чате с ботом.")
        return
    if not command.args or not str(command.args).strip():
        await message.answer("Использование: /token <jwt>")
        return
    token = str(command.args).strip()
    if not is_valid_token(token):
        await message.answer("Токен недействителен или истёк. Получите новый в Auth Service.")
        return
    r = get_redis()
    await r.set(jwt_storage_key(message.from_user.id), token)
    await message.answer("Токен принят и сохранён.")


@router.message(F.text)
async def text_message(message: Message) -> None:
    if message.from_user is None:
        return
    text = (message.text or "").strip()
    if text.startswith("/"):
        await message.answer("Неизвестная команда. Для привязки токена: /token <jwt>")
        return

    r = get_redis()
    key = jwt_storage_key(message.from_user.id)
    stored = await r.get(key)
    if not stored:
        await message.answer(
            "Нет сохранённого токена. Зарегистрируйтесь и возьмите JWT в Auth Service, "
            f"затем отправьте: /token <jwt>\nДокументация: {_auth_swagger_url()}"
        )
        return
    if not is_valid_token(stored):
        await message.answer("Сохранённый токен недействителен. Отправьте новый: /token <jwt>")
        return

    llm_request.delay(message.chat.id, text)
    await message.answer("Запрос принят, ответ придёт в этом чате.")
