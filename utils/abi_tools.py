# utils/abi_tools.py

from eth_abi import encode_abi
import asyncio

def encode_transfer(to_address: str, amount: int) -> str:
    method_id = "0xa9059cbb"  # transfer(address,uint256)
    to_padded = to_address.lower().replace("0x", "").zfill(64)
    value_padded = hex(amount)[2:].zfill(64)
    return "0x" + method_id + to_padded + value_padded
