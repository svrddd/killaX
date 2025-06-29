import datetime
import os
import aiohttp
import asyncio

# Глобальные счётчики
stats = {
    "checked": 0,
    "vulnerable": 0,
    "attacked": 0
}

# Telegram токен и чат ID
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def log_info(message: str):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] [INFO] {message}")

    message_lower = message.lower()

    if "анализ tx" in message_lower:
        stats["checked"] += 1
    elif "найдены уязвимости" in message_lower:
        stats["vulnerable"] += 1
    elif "атака отправлена" in message_lower or "📤 tx отправлена" in message_lower:
        stats["attacked"] += 1

async def send_telegram_message(text: str):
    """
    Универсальная функция отправки Telegram-сообщений
    """
    if not TG_TOKEN or not TG_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e:
        print(f"[ERROR] Не удалось отправить сообщение в Telegram: {e}")

async def send_hourly_report():
    """
    Отправляет Telegram-репорт и сбрасывает счётчики.
    """
    if not TG_TOKEN or not TG_CHAT_ID:
        return

    msg = (
        "🕒 <b>Hourly DrainBot Report</b>\n"
        f"🔍 Checked contracts: <b>{stats['checked']}</b>\n"
        f"⚠️ Vulnerable found: <b>{stats['vulnerable']}</b>\n"
        f"🚀 Attacks launched: <b>{stats['attacked']}</b>"
    )

    await send_telegram_message(msg)

    # Сброс статистики
    for key in stats:
        stats[key] = 0

