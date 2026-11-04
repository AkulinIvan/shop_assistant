"""
Запуск Telegram-бота. Запускать из корня проекта:
    python run_bot.py
"""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.bot import main  # noqa: E402

if __name__ == "__main__":
    asyncio.run(main())