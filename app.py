from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import requests

app = Flask(__name__)

SECRET_KEY = 'a70c4db643d8b4b629881c7ad33bd76e5e51b26b'
SHOP_ID = '708799d5-e970-4909-ae4e-b4f9a03ee1b4'
LAVA_URL = 'https://api.lava.ru/business/invoice/create'

@app.route('/pay', methods=['POST'])
def pay():
    try:
        data = request.get_json()

        payload = {
            "shopId": SHOP_ID,
            "sum": int(data["sum"]),
            "orderId": data["orderId"],
            "hookUrl": "https://example.com/hook",
            "successUrl": "https://example.com/success",
            "failUrl": "https://example.com/fail",
            "expire": 300,
            "comment": f"Оплата от Telegram: {data['client_id']}",
            "customFields": json.dumps({"telegram_id": data["client_id"]}),
            "includeService": ["card", "sbp", "qiwi"]
        }

        json_string = json.dumps(payload, separators=(',', ':'))
        signature = hmac.new(SECRET_KEY.encode(), json_string.encode(), hashlib.sha256).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Signature': signature
        }

        response = requests.post(LAVA_URL, headers=headers, data=json_string)
        return jsonify({"status": "ok", "lava": response.json()})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
