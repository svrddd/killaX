import aiohttp
from config.rpc_endpoints import RPC_HTTP_ENDPOINTS
from utils.logger import log_info
from eth_utils import keccak, to_checksum_address
from rlp import encode as rlp_encode

async def get_storage_at(network: str, address: str, slot: int) -> str:
    """
    Получает значение storage по указанному слоту.
    """
    url = RPC_HTTP_ENDPOINTS[network]
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getStorageAt",
        "params": [address, hex(slot), "latest"],
        "id": 1,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=10) as resp:
                data = await resp.json()
                return data.get("result", "0x")
    except Exception as e:
        log_info(f"[{network}] ⚠️ Ошибка при чтении storage: {e}")
        return "0x"

async def is_eoa(network: str, address: str) -> bool:
    """
    Проверяет, является ли адрес EOA (если код контракта пустой).
    """
    url = RPC_HTTP_ENDPOINTS[network]
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getCode",
        "params": [address, "latest"],
        "id": 1,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                data = await resp.json()
                code = data.get("result", "")
                return code == "0x"
    except Exception as e:
        log_info(f"[{network}] ⚠️ Ошибка при проверке EOA: {e}")
        return False

def calculate_create_address(sender: str, nonce: int) -> str:
    """
    Вычисляет адрес создаваемого контракта (CREATE).
    """
    if sender.startswith("0x"):
        sender = sender[2:]
    sender_bytes = bytes.fromhex(sender)

    try:
        nonce_int = int(nonce)
    except Exception:
        log_info(f"⚠️ Неверный nonce: {nonce} — используется 0")
        nonce_int = 0

    encoded = rlp_encode([sender_bytes, nonce_int])
    return to_checksum_address(keccak(encoded)[12:])


