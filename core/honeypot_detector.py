# core/honeypot_detector.py

import aiohttp
from config.rpc_endpoints import RPC_HTTP_ENDPOINTS
from utils.logger import log_info

async def simulate_dry_run(network: str, from_address: str, contract_address: str, data: str) -> bool:
    """
    Выполняет dry-run вызов (eth_call) для проверки, не является ли контракт honeypot'ом.
    """
    url = RPC_HTTP_ENDPOINTS[network]
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "from": from_address,
                "to": contract_address,
                "data": data,
            },
            "latest"
        ],
        "id": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=5) as resp:
                result = await resp.json()
                if "result" in result:
                    return True  # dry-run прошёл успешно
                log_info(f"[{network}] 🔒 Honeypot dry-run error: {result}")
    except Exception as e:
        log_info(f"[{network}] 🧱 Honeypot вызов завершился ошибкой: {e}")

    return False

