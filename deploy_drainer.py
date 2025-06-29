import sys
import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
from eth_account import Account
from solcx import compile_source, install_solc
from config.settings import PRIVATE_KEY
from config.rpc_endpoints import RPC_HTTP_ENDPOINTS

install_solc("0.8.19")

with open("contracts/Drainer.sol", "r") as f:
    source_code = f.read()

compiled = compile_source(source_code, output_values=["abi", "bin"], solc_version="0.8.19")
contract_interface = list(compiled.values())[0]
ABI = contract_interface["abi"]
BYTECODE = contract_interface["bin"]

async def deploy(network: str):
    if network not in RPC_HTTP_ENDPOINTS:
        print(f"[ERROR] Сеть {network} не найдена в RPC_HTTP_ENDPOINTS")
        return

    w3 = AsyncWeb3(AsyncHTTPProvider(RPC_HTTP_ENDPOINTS[network]))
    account = Account.from_key(PRIVATE_KEY)
    sender = account.address

    nonce = await w3.eth.get_transaction_count(sender)
    gas_price = await w3.eth.gas_price

    tx = {
        "from": sender,
        "nonce": nonce,
        "gas": 1_500_000,
        "gasPrice": gas_price,
        "data": "0x" + BYTECODE,
        "chainId": await w3.eth.chain_id,
    }

    signed_tx = account.sign_transaction(tx)
    tx_hash = await w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"[{network.upper()}] ⏳ TX sent: {tx_hash.hex()}")

    receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[{network.upper()}] ✅ Contract deployed at: {receipt.contractAddress}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_drainer.py <network>")
        sys.exit(1)

    net = sys.argv[1].lower()
    asyncio.run(deploy(net))
