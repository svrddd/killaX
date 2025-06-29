from dotenv import load_dotenv
import os

load_dotenv()

print("✅ DEBUG: ARBITRUM WSS =", os.getenv("RPC_WS_ARBITRUM_BLAST"))
print("✅ DEBUG: BASE WSS =", os.getenv("RPC_WS_BASE_BLAST"))
print("✅ DEBUG: BSC WSS =", os.getenv("RPC_WS_BSC_BLAST"))

import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

def log_env(key: str):
    value = os.getenv(key)
    if not value:
        print(f"[⚠️ WARNING] Переменная {key} не найдена в .env")
    return value

RPC_HTTP_ENDPOINTS = {
    "arbitrum": [
        log_env("RPC_HTTP_ARBITRUM_BLAST"),
        log_env("RPC_HTTP_ARBITRUM_ALCHEMY"),
    ],
    "base": [
        log_env("RPC_HTTP_BASE_BLAST"),
        log_env("RPC_HTTP_BASE_ALCHEMY"),
    ],
    "bsc": [
        log_env("RPC_HTTP_BSC_BLAST"),
        log_env("RPC_HTTP_BSC_ALCHEMY"),
    ],
}

RPC_WS_ENDPOINTS = {
    "arbitrum": [
        log_env("RPC_WS_ARBITRUM_BLAST"),
        log_env("RPC_WS_ARBITRUM_ALCHEMY"),
    ],
    "base": [
        log_env("RPC_WS_BASE_BLAST"),
        log_env("RPC_WS_BASE_ALCHEMY"),
    ],
    "bsc": [
        log_env("RPC_WS_BSC_BLAST"),
        log_env("RPC_WS_BSC_ALCHEMY"),
    ],
}
