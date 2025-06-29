import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

from utils.tx_utils import get_transaction_by_hash
from utils.evm_utils import calculate_create_address
from core.analyzer import analyze_contract
from utils.logger import log_info
from config.rpc_endpoints import RPC_WS_ENDPOINTS

load_dotenv()

SUBSCRIPTION_PAYLOAD = {
    "jsonrpc": "2.0",
    "method": "eth_subscribe",
    "params": ["newPendingTransactions"],
    "id": 1
}


async def start_subscription(network_name: str, wss_url: str):
    while True:
        try:
            async with websockets.connect(wss_url, ping_interval=60, ping_timeout=30) as ws:
                log_info(f"[{network_name.upper()}] ✅ Подключен к WSS {wss_url}")
                await ws.send(json.dumps(SUBSCRIPTION_PAYLOAD))

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if "params" in data and "result" in data["params"]:
                        tx_hash = data["params"]["result"]
                        log_info(f"[{network_name}] 🆕 TX: {tx_hash}")

                        tx_data = await get_transaction_by_hash(network_name, tx_hash)
                        if not tx_data:
                            continue

                        sender = tx_data.get("from", "0x0")
                        to = tx_data.get("to")
                        nonce_raw = tx_data.get("nonce", 0)

                        try:
                            nonce = int(nonce_raw, 16) if isinstance(nonce_raw, str) else int(nonce_raw)
                        except Exception:
                            log_info(f"[{network_name}] ⚠️ Невалидный nonce: {nonce_raw} — пропуск")
                            continue

                        if to is None:
                            contract_address = calculate_create_address(sender, nonce)
                            init_code = tx_data.get("input", "0x")

                            await analyze_contract(
                                network=network_name,
                                tx_hash=tx_hash,
                                init_code=init_code,
                                contract_address=contract_address,
                                sender=sender
                            )
        except Exception as e:
            log_info(f"[{network_name}] ⚠️ Ошибка при подключении к {wss_url}: {e}")
            await asyncio.sleep(5)  # Реконнект через 5 сек


async def run_all_watchers():
    tasks = []
    for network, urls in RPC_WS_ENDPOINTS.items():
        if not isinstance(urls, list):
            log_info(f"[{network}] ❌ URLs не список — скип: {urls}")
            continue

        valid_urls = [url for url in urls if isinstance(url, str) and url.startswith("wss://")]
        if not valid_urls:
            log_info(f"[{network}] ❌ Нет валидных WSS URL — скип")
            continue

        for url in valid_urls:
            log_info(f"[{network}] 📡 Запуск подписки на {url}")
            tasks.append(asyncio.create_task(start_subscription(network, url)))

    await asyncio.gather(*tasks)


