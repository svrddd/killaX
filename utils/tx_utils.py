import aiohttp
import json
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address
from web3 import Web3
import asyncio

from config.rpc_endpoints import RPC_HTTP_ENDPOINTS
from config.settings import PRIVATE_KEY, GAS_BUMP_ENABLED, GAS_BUMP_PERCENT
from utils.logger import log_info

Account.enable_unaudited_hdwallet_features()

def bump_gas(value: int, percent: int = 30) -> int:
    return int(value * (100 + percent) / 100)

def get_valid_rpc_urls(network: str) -> list:
    urls = RPC_HTTP_ENDPOINTS.get(network, [])
    return [u for u in urls if isinstance(u, str) and u.startswith("http")]

async def build_and_send_tx(network: str, to_address: str, data: str, value: int = 0) -> str:
    try:
        urls = get_valid_rpc_urls(network)
        if not urls:
            raise ValueError(f"Нет валидных RPC URL для сети '{network}'")
        url = urls[0]

        sender = Account.from_key(PRIVATE_KEY).address
        sender_checksum = to_checksum_address(sender)

        async with aiohttp.ClientSession() as session:
            nonce_payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [sender_checksum, "pending"],
                "id": 1
            }
            async with session.post(url, json=nonce_payload) as resp:
                nonce_data = await resp.json()
                nonce = int(nonce_data["result"], 16)

            gas_price_payload = {
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 1
            }
            async with session.post(url, json=gas_price_payload) as resp:
                gas_data = await resp.json()
                base_gas_price = int(gas_data["result"], 16)

            gas_price = bump_gas(base_gas_price, GAS_BUMP_PERCENT) if GAS_BUMP_ENABLED else base_gas_price

            log_info(f"[{network}] ⛽ Gas price: base = {base_gas_price // 10**9} gwei | final = {gas_price // 10**9} gwei")

            tx = {
                "to": to_address,
                "value": value,
                "gas": 300000,
                "gasPrice": gas_price,
                "nonce": nonce,
                "data": data,
                "chainId": await get_chain_id(session, url)
            }

            signed_tx = Account.sign_transaction(tx, PRIVATE_KEY)
            raw_tx_hex = signed_tx.rawTransaction.hex()

            send_payload = {
                "jsonrpc": "2.0",
                "method": "eth_sendRawTransaction",
                "params": [raw_tx_hex],
                "id": 1
            }

            async with session.post(url, json=send_payload) as resp:
                send_data = await resp.json()
                tx_hash = send_data.get("result", None)

                if not tx_hash:
                    raise Exception(send_data.get("error", {}).get("message", "Unknown error"))

                return tx_hash

    except Exception as e:
        log_info(f"[{network}] ❌ Ошибка сборки/отправки TX: {e}")
        raise

async def get_transaction_by_hash(network: str, tx_hash: str) -> dict:
    urls = get_valid_rpc_urls(network)
    if not urls:
        raise ValueError(f"Нет RPC для сети '{network}'")

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [tx_hash],
        "id": 1,
    }

    async def try_url(url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=5) as resp:
                    tx_data = await resp.json()
                    result = tx_data.get("result")
                    if result:
                        log_info(f"[{network}] ✅ Найдена транза {tx_hash[:10]} на {url}")
                        return result
                    else:
                        log_info(f"[{network}] ⛔ Нет транзы {tx_hash[:10]} на {url}")
        except Exception as e:
            log_info(f"[{network}] ❌ Ошибка {tx_hash[:10]} на {url}: {e}")
        return None

    results = await asyncio.gather(*(try_url(u) for u in urls))
    for res in results:
        if res:
            return res

    log_info(f"[{network}] ❌ Транзакция {tx_hash[:10]} не найдена ни на одном RPC")
    return {}

async def get_chain_id(session, url: str) -> int:
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_chainId",
        "params": [],
        "id": 1,
    }
    async with session.post(url, json=payload, timeout=5) as resp:
        data = await resp.json()
        return int(data["result"], 16)

