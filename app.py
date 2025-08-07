from flask import Flask, request, jsonify
import hmac
import hashlib
import requests
import json

app = Flask(__name__)

# 🔐 Секретный ключ и ID проекта из Lava
SECRET_KEY = "a70c4db643d8b4b629881c7ad33bd76e5e51b26b"
SHOP_ID = "708799d5-e970-4909-ae4e-b4f9a03ee1b4"
LAVA_URL = "https://api.lava.ru/business/invoice/create"

@app.route("/", methods=["GET"])
def index():
    return "✅ Flask API работает. Отправь POST-запрос на /pay"

@app.route("/pay", methods=["POST"])
def create_invoice():
    try:
        data = request.get_json()

        payload = {
            "shopId": SHOP_ID,
            "sum": data.get("summa", 1),
            "orderId": data.get("идентификатор заказа", "order_" + str(data.get("идентификатор клиента"))),
            "hookUrl": "https://example.com/hook",
            "successUrl": "https://example.com/success",
            "failUrl": "https://example.com/fail",
            "expire": 300,
            "comment": f"Оплата от Telegram: {data.get('идентификатор клиента')}",
            "customFields": json.dumps({"telegram_id": data.get("идентификатор клиента")}),
            "includeService": ["card", "sbp", "qiwi"]
        }

        json_payload = json.dumps(payload, ensure_ascii=False)
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
        lava_response = response.json()

        return jsonify({
            "status": "ok",
            "lava": lava_response
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
