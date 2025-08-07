from flask import Flask, request, jsonify
import hashlib
import hmac
import json
import requests

app = Flask(__name__)

SECRET_KEY = "a70c4db643d8b4b629881c7ad33bd76e5e51b26b"
SHOP_ID = "708799d5-e970-4909-ae4e-b4f9a03ee1b4"
LAVA_URL = "https://api.lava.ru/business/invoice/create"

@app.route("/pay", methods=["POST"])
def create_invoice():
    try:
        data = request.json
        payload = {
            "shopId": SHOP_ID,
            "sum": data["сумма"],
            "orderId": data["идентификатор заказа"],
            "hookUrl": "https://example.com/hook",
            "successUrl": "https://example.com/success",
            "failUrl": "https://example.com/fail",
            "expire": 300,
            "comment": f"Оплата от Telegram: {data['идентификатор клиента']}",
            "customFields": json.dumps({ "telegram_id": data["идентификатор клиента"] }, ensure_ascii=False),
            "includeService": ["card", "sbp", "qiwi"]
        }

        json_payload = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            json_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Signature": signature
        }

        response = requests.post(LAVA_URL, data=json_payload.encode("utf-8"), headers=headers)
        result = response.json()

        return jsonify({
            "статус": "ok",
            "лава": result
        })

    except Exception as e:
        return jsonify({
            "статус": "error",
            "ошибка": str(e)
        }), 500