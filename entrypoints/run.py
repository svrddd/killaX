import sys
import os
import asyncio
from dotenv import load_dotenv

# Добавление пути к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from config.settings import TELEGRAM_HOURLY_REPORT_ENABLED
from utils.logger import log_info, send_hourly_report
from core.watcher import run_all_watchers  # исправлено

async def hourly_scheduler():
    while True:
        await asyncio.sleep(3600)  # 1 час
        if TELEGRAM_HOURLY_REPORT_ENABLED:
            await send_hourly_report()

async def start_bot():
    log_info("🚀 DrainBot started")

    while True:
        try:
            await asyncio.gather(
                run_all_watchers(),
                hourly_scheduler()
            )
        except Exception as e:
            log_info(f"[MAIN] ⚠️ Бот упал: {e}. Перезапуск через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        log_info("🛑 DrainBot stopped manually.")

