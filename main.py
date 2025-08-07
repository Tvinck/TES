from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import requests
import time

app = Flask(__name__)

SECRET_KEY = 'a70c4db643d8b4b629881c7ad33bd76e5e51b26b'
SHOP_ID = '708799d5-e970-4909-ae4e-b4f9a03ee1b4'
LAVA_URL = 'https://api.lava.ru/business/invoice/create'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        sum_val = data.get("sum")
        order_id = data.get("orderId") or "order_" + str(int(time.time()))
        client_id = str(data.get("client_id", "unknown"))

        payload = {
            "shopId": SHOP_ID,
            "sum": sum_val,
            "orderId": order_id,
            "hookUrl": "https://example.com/hook",
            "successUrl": "https://example.com/success",
            "failUrl": "https://example.com/fail",
            "expire": 300,
            "comment": f"Оплата от Telegram: {client_id}",
            "customFields": {
                "telegram_id": client_id
            },
            "includeService": ["card", "sbp", "qiwi"]
        }

        json_data = json.dumps(payload, separators=(',', ':'))
        signature = hmac.new(SECRET_KEY.encode(), json_data.encode(), hashlib.sha256).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Signature': signature
        }

        lava_response = requests.post(LAVA_URL, data=json_data, headers=headers)
        lava_json = lava_response.json()

        if lava_json.get("data") and lava_json["data"].get("invoice_url"):
            return jsonify({
                "status": "ok",
                "invoice_url": lava_json["data"]["invoice_url"]
            })
        else:
            return jsonify({
                "status": "error",
                "message": lava_json.get("error", "Unknown error"),
                "lava_response": lava_json
            }), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
