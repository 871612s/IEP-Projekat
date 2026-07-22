from web3 import Web3
from web3 import HTTPProvider
from os import environ
import os
import json
from datetime import datetime
from bson import ObjectId
from app import redis_client, assets

web3 = Web3(HTTPProvider(environ["GANACHE_RPC_URL"]))

def read_file(path):
    with open(path) as f:
        return f.read()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
abi = read_file(os.path.join(BASE_DIR, "Voting.abi"))
bytecode = read_file(os.path.join(BASE_DIR, "Voting.bin"))

contract = web3.eth.contract(
    abi=abi,
    bytecode=bytecode
)

def deploy_contract(voters, owner):
    transaction_hash = contract.constructor(voters).transact({
        "from": owner
    })

    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

    return receipt.contractAddress

def build_approve_transaction(contract_address, voter):
    return get_contract(contract_address).functions.approve().build_transaction({
        "from": voter,
        "nonce": web3.eth.get_transaction_count(voter),
        "gasPrice": web3.eth.gas_price,
    })

def build_reject_transaction(contract_address, voter):
    return get_contract(contract_address).functions.reject().build_transaction({
        "from": voter,
        "nonce": web3.eth.get_transaction_count(voter),
        "gasPrice": web3.eth.gas_price,
    })

def get_status(contract_address):
    return get_contract(contract_address).functions.status().call()

def get_contract(contract_address):
    return web3.eth.contract(
        address=contract_address,
        abi=abi
    )

def process_finished_votes():
    for key in redis_client.scan_iter():

        lock_key = f"processing_lock:{key}"
        # Atomarno pokušaj da zaključaš ovaj ključ; ako neko drugi već radi na njemu, preskoči
        if not redis_client.set(lock_key, "1", nx=True, ex=10):
            continue

        try:
            value = redis_client.get(key)

            if value is None:
                continue

            order = json.loads(value)

            if "contract" not in order:
                continue

            status = get_status(order["contract"])

            if status == 0:
                continue

            if status == 1:

                if order["order_type"] == "BUY":

                    asset = {
                        "name": order["name"],
                        "categories": order["categories"],
                        "buying_price": order["buying_price"],
                        "buying_date": datetime.utcnow(),
                        "selling_price": None,
                        "selling_date": None,
                        "info": order["info"]
                    }

                    assets.insert_one(asset)

                else:

                    assets.update_one(
                        {
                            "_id": ObjectId(order["id"])
                        },
                        {
                            "$set": {
                                "selling_price": order["selling_price"],
                                "selling_date": datetime.utcnow()
                            }
                        }
                    )

                redis_client.delete(key)
            elif status == 2:
                redis_client.delete(key)
        finally:
            redis_client.delete(lock_key)