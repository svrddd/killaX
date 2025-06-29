from web3 import Web3
import os

w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org"))  # вставь RPC

private_key = os.getenv("PRIVATE_KEY")
account = w3.eth.account.from_key(private_key)

contract_address = Web3.to_checksum_address("0x981818Bb1B4C9Ee8640dB57afF459517c9285bC5")
abi = [
    {
        "inputs": [],
        "name": "sweep",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=contract_address, abi=abi)
tx = contract.functions.sweep().build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gas": 100_000,
    "gasPrice": w3.eth.gas_price
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("TX hash:", w3.to_hex(tx_hash))
