# core/stats.py

checked_contracts = 0
vulnerable_found = 0
successful_attacks = 0
total_profit = 0.0  # можно убрать, если пока не считаем

def reset_stats():
    global checked_contracts, vulnerable_found, successful_attacks, total_profit
    checked_contracts = 0
    vulnerable_found = 0
    successful_attacks = 0
    total_profit = 0.0
