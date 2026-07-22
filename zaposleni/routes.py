from flask import request, jsonify
from bson import ObjectId
from app import application, assets, redis_client
from roles import Roles
from decorators import role_check
from datetime import datetime
import uuid
import json


def parse_object_id(value):
    try:
        return ObjectId(value)
    except:
        return None
    
def format_date(dt):
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"
    
@application.route("/search",methods=["POST"])
@role_check(Roles.EMPLOYEE)
def search():
    data = request.get_json() or {}
    name = data.get("name")
    category = data.get("category")
    buying_date = data.get("buying_date")
    selling_date = data.get("selling_date")
    info_filters = data.get("info_filters") or []
    query = {}
    
    if name:
        query["name"] = {
            "$regex": name,
            "$options": "i"
        }
    if category:
        query["categories"] = category
    
    if buying_date:
        query["buying_date"] = {
            "$gt": datetime.fromisoformat(
                buying_date.replace("Z","+00:00")
            )
        }
        
    if selling_date:
        query["selling_date"] = {
            "$lt": datetime.fromisoformat(
                selling_date.replace("Z","+00:00")
            )
        }    
    
    for f in info_filters:
        query["info." + f["field"]] = {
            "$" + f["operator"]: f["value"]
        }
    
    documents = list(assets.find(query))
    
    result = []

    for asset in documents:

        asset["id"] = str(asset["_id"])
        del asset["_id"]

        asset["buying_date"] = format_date(asset.get("buying_date"))

        if asset.get("selling_price") is not None and asset.get("selling_date") is not None:
            asset["selling_date"] = format_date(asset["selling_date"])
        else:
            asset.pop("selling_price", None)
            asset.pop("selling_date", None)

        result.append(asset)

    return jsonify({"assets":result})

@application.route("/create_buy_order", methods=["POST"])
@role_check(Roles.EMPLOYEE)
def create_buy_order():
    data = request.get_json() or {}
    
    name = data.get("name")
    categories = data.get("categories")
    buying_price = data.get("buying_price")
    info = data.get("info")
    
    if not name:
        return jsonify(message="Field name is missing."), 400
    
    if categories is None:
        return jsonify(message="Field categories is missing."), 400
    
    if buying_price is None:
        return jsonify(message="Field buying_price is missing."), 400
    
    if info is None:
        return jsonify(message="Field info is missing."), 400
    
    if not isinstance(info, dict):
        return jsonify(message="Field info is missing."), 400

    if not isinstance(categories, list):
        return jsonify(message="Categories list is empty."), 400
        
    if len(categories) == 0:
        return jsonify(message="Categories list is empty."), 400
    
    if not isinstance(buying_price, (int,float)) or buying_price <= 0:
        return jsonify(message="Invalid buying price."), 400
    
    
    order = {
        "uuid": str(uuid.uuid4()),
        "order_type": "BUY",
        "name": name,
        "categories": categories,
        "buying_price": buying_price,
        "info": info
    }
    
    redis_client.set(
        order["uuid"],
        json.dumps(order)
    )
    
    return "", 200

@application.route("/create_sell_order", methods=["POST"])
@role_check(Roles.EMPLOYEE)
def create_sell_order():
    
    data = request.get_json() or {}
    
    id = data.get("id")
    selling_price = data.get("selling_price")
    
    
    
    if not id:
        return jsonify(message="Field id is missing."), 400
    
    if not isinstance(id,str):
        return jsonify(message="Invalid id."), 400
    
    if selling_price is None:
        return jsonify(message="Field selling_price is missing."), 400
    
    object_id = parse_object_id(id)
    
    if object_id is None:
        return jsonify(message="Invalid id."), 400
    
    asset = assets.find_one(
        {
            "_id": object_id
        }
    )
    
    if asset is None:
        return jsonify(message="Invalid id."), 400
    
    if not isinstance(selling_price, (int, float)) or selling_price <= 0:
        return jsonify(message="Invalid selling price."), 400
    
    order = {
        "uuid": str(uuid.uuid4()),
        "order_type": "SELL",
        "id": id,
        "selling_price": selling_price
    }
    
    redis_client.set(
        order["uuid"],
        json.dumps(order)
    )
    
    return "", 200
