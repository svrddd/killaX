# core/initcode_simulator.py
import asyncio

from utils.logger import log_info
from config.settings import VULNERABLE_SIGNATURES

def extract_4byte_selectors_from_initcode(bytecode: str) -> list:
    """
    Извлекает возможные 4byte сигнатуры функций из initCode (байткод до деплоя).
    """
    selectors = []
    for i in range(0, len(bytecode) - 8, 2):
        if bytecode[i:i+2] in ("60", "63"):  # PUSH1/PUSH4
            selector = bytecode[i+2:i+10]
            if len(selector) == 8:
                selectors.append(selector.lower())
    return list(set(selectors))

def simulate_initcode(bytecode: str) -> dict:
    """
    Имитирует поведение будущего контракта: ищет сигнатуры уязвимостей.
    Возвращает {'ok': bool, 'matched': list}
    """
    bytecode = bytecode[2:] if bytecode.startswith("0x") else bytecode
    found = extract_4byte_selectors_from_initcode(bytecode)

    matched = []
    for selector in found:
        for vuln_name, vuln_sigs in VULNERABLE_SIGNATURES.items():
            if selector in vuln_sigs:
                matched.append((vuln_name, selector))

    result = {
        "ok": bool(matched),
        "matched": matched
    }

    if matched:
        log_info(f"[INITCODE] ⚠️ Уязвимости до деплоя: {matched}")
    else:
        log_info(f"[INITCODE] ✅ Безопасен до деплоя")

    return result
