import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.core.config import settings


def build() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    return bot, dp


async def start_polling() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN пуст — укажите в .env")
    bot, dp = build()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_polling())
