from flask import request, jsonify
from bson import ObjectId
from app import application, assets, redis_client
from roles import Roles
from decorators import role_check
from datetime import datetime
import json
import uuid
from web3 import Web3
import blockchain

@application.route("/pending_orders", methods=["GET"])
@role_check(Roles.DIRECTOR)
def pending_orders():
    keys = redis_client.scan_iter()
    orders = []
    
    for key in keys:
        value = redis_client.get(key)
        orders.append(json.loads(value))
    
    return jsonify(
        {
            "orders":orders
        }
    )
    
@application.route("/decision", methods=["POST"])
@role_check(Roles.DIRECTOR)
def decision():
    data = request.get_json() or {}
    
    uuid_str = data.get("uuid")
    voters = data.get("voters")
    
    if not uuid_str:
        return jsonify(message="Field uuid is missing."), 400
    
    try:
        uuid.UUID(uuid_str)
    except:
        return jsonify(message="Invalid uuid."),400
    
    value = redis_client.get(uuid_str)
    
    if value is None:
        return jsonify(message="Invalid uuid."), 400
    
    if voters is None or len(voters) == 0:
        return jsonify(message="Field voters is missing."), 400
    
    for voter in voters:
        if not Web3.is_address(voter):
            return jsonify(message="Invalid voter address."), 400
    
    if len(voters) % 2 == 0:
        return jsonify(message="Even number of voters."), 400
    
    contract_address = blockchain.deploy_contract(
        voters,
        blockchain.web3.eth.accounts[0]
    )
    
    order = json.loads(value)
    
    order["contract"] = contract_address
    
    redis_client.set(
        uuid_str,
        json.dumps(order)
    )
    
    approve_transaction = blockchain.build_approve_transaction(
        contract_address=contract_address,
        voter=voters[0]
    )
    
    reject_transaction = blockchain.build_reject_transaction(
        contract_address=contract_address,
        voter=voters[0]
    )
        
    return jsonify(
        approve_transaction=approve_transaction,
        reject_transaction=reject_transaction
    ), 200

@application.route("/report",methods=["GET"])
@role_check(Roles.DIRECTOR)
def report():
    pipeline = [
        {
            "$unwind": "$categories"
        },
        {
            "$group":{
                "_id": "$categories",
                "spent": {
                    "$sum": "$buying_price"
                },
                "earned": {
                    "$sum":{
                        "$cond" :[
                            {
                                "$and":[
                                    {
                                        "$ne": [
                                            "$selling_price", None
                                        ]
                                    },
                                    {
                                        "$ne":[
                                            "$selling_date", None
                                        ]
                                    }
                                ]
                            },
                            "$selling_price",
                            0
                        ]
                    }
                }
            }
        },
        {
            "$project":{
                "_id": 0,
                "category": "$_id",
                "spent": 1,
                "earned": 1
            }
        },
        {
            "$sort":{
                "earned": -1,
                "spent": 1,
                "category": 1
            }
        }
    ]
    
    statistics = list(
        assets.aggregate(pipeline)
    )
    
    return jsonify(
        {
            "statistics": statistics
        }
    )