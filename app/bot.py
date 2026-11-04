"""
Telegram-бот поверх AssistantService.
Вся логика ответов и защита от галлюцинаций — в service.py / БД.
Здесь только транспорт: принять сообщение → отдать в service → ответить.
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

from app.service import AssistantService

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("bot")

dp = Dispatcher()
svc = AssistantService()

WELCOME = (
    "Здравствуйте! Я ассистент интернет-магазина.\n"
    "Отвечаю по регламенту: товар, доставка, возврат, брак, скидки.\n"
    "Если вопрос вне регламента — честно скажу и предложу уточнить у менеджера."
)


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(WELCOME)


@dp.message(Command("help"))
async def on_help(message: Message) -> None:
    await message.answer(
        "Примеры вопросов:\n"
        "• сколько стоят наушники X1?\n"
        "• какая доставка?\n"
        "• можно вернуть вскрытые наушники?\n"
        "• что с браком?\n"
        "• есть ли скидка?"
    )


@dp.message(F.text)
async def on_text(message: Message) -> None:
    question = (message.text or "").strip()
    if not question:
        return
    log.info("Q: %s", question)
    try:
        result = svc.ask(question)
    except Exception:
        log.exception("service error")
        await message.answer(
            "Извините, произошла техническая ошибка. "
            "Попробуйте ещё раз или свяжитесь с менеджером."
        )
        return

    answer = result["answer"]
    log.info("A: %s [%s]", answer, result["source"])
    await message.answer(answer)


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN не задан. Создайте .env по образцу .env.example")
    bot = Bot(token=token)
    log.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())