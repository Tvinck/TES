from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import json

app = Flask(__name__)

SECRET_KEY = 'a70c4db643d8b4b629881c7ad33bd76e5e51b26b'
LAVA_URL = 'https://api.lava.ru/business/invoice/create'
SHOP_ID = '708799d5-e970-4909-ae4e-b4f9a03ee1b4'

@app.route('/pay', methods=['POST'])
def create_invoice():
    try:
        data = request.json
        payload = {
            "shopId": SHOP_ID,
            "sum": data["sum"],
            "orderId": data["orderId"],
            "hookUrl": "https://example.com/hook",
            "successUrl": "https://example.com/success",
            "failUrl": "https://example.com/fail",
            "expire": 300,
            "comment": f"Оплата от Telegram: {data['client_id']}",
            "customFields": json.dumps({"telegram_id": data["client_id"]}),
            "includeService": ["card", "sbp"]
        }

        json_data = json.dumps(payload, separators=(',', ':'))
        signature = hmac.new(
            SECRET_KEY.encode('utf-8'),
            json_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Signature": signature
        }

        response = requests.post(LAVA_URL, data=json_data, headers=headers)
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
