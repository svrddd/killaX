# core/hourly_report.py

import asyncio
from core.stats import checked_contracts, vulnerable_found, successful_attacks, reset_stats
from utils.logger import send_telegram_message

async def hourly_report():
    while True:
        await asyncio.sleep(3600)

        msg = (
            f"📊 Ежечасный отчёт:\n"
            f"🔎 Проверено контрактов: {checked_contracts}\n"
            f"🛠️ Найдено уязвимых: {vulnerable_found}\n"
            f"💥 Атак выполнено: {successful_attacks}\n"
        )

        await send_telegram_message(msg)
        reset_stats()

