import aiohttp
from config.rpc_endpoints import RPC_HTTP_ENDPOINTS
from utils.logger import log_info
from config.tokens import ERC20_TOKENS  # Формат: {"bsc": [{"address": "...", "symbol": "...", "decimals": 18}], ...}

async def get_native_balance(address: str, network: str) -> float:
    url = RPC_HTTP_ENDPOINTS[network]
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=5) as resp:
                data = await resp.json()
                balance_wei = int(data.get("result", "0x0"), 16)
                return balance_wei / 10**18
    except Exception as e:
        log_info(f"[{network}] ⚠️ Ошибка при получении баланса: {e}")
        return 0.0

async def get_erc20_balance(token_address: str, wallet_address: str, network: str, decimals: int = 18) -> float:
    url = RPC_HTTP_ENDPOINTS[network]
    method_id = "0x70a08231"
    padded_address = wallet_address.lower().replace("0x", "").zfill(64)
    data = method_id + padded_address

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": token_address,
            "data": data
        }, "latest"],
        "id": 1,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=5) as resp:
                response = await resp.json()
                balance_raw = int(response.get("result", "0x0"), 16)
                return balance_raw / (10 ** decimals)
    except Exception as e:
        log_info(f"[{network}] ⚠️ Ошибка ERC20-баланса {token_address}: {e}")
        return 0.0

async def get_all_token_balances(wallet_address: str, network: str) -> dict:
    balances = {}
    tokens = ERC20_TOKENS.get(network, [])

    for token in tokens:
        try:
            amount = await get_erc20_balance(token["address"], wallet_address, network, token.get("decimals", 18))
            if amount > 0:
                balances[token["symbol"]] = round(amount, 6)
        except Exception as e:
            log_info(f"[{network}] ⚠️ Ошибка баланса токена {token['symbol']}: {e}")

    return balances

