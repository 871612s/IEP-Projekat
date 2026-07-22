from flask import request, jsonify
from bson import ObjectId
from app import application, assets, redis_client
from roles import Roles
from datetime import datetime



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
def search():
    data = request.get_json() or {}
    min_price = data.get("min_price")
    max_price = data.get("max_price")
    
    query = {}
    
    if min_price is not None or max_price is not None:
        query["buying_price"] = {}

    if min_price is not None:
        query["buying_price"]["$gte"] = min_price

    if max_price is not None:
        query["buying_price"]["$lte"] = max_price
    
    
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
