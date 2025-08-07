
from flask import Flask, request, jsonify
import hashlib
import hmac
import json
import requests

app = Flask(__name__)

SECRET_KEY = 'a70c4db643d8b4b629881c7ad33bd76e5e51b26b'
SHOP_ID = '708799d5-e970-4909-ae4e-b4f9a03ee1b4'
LAVA_URL = 'https://api.lava.ru/business/invoice/create'

@app.route("/pay", methods=["POST"])
def create_invoice():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Empty request"}), 400

        payload = {
            "shopId": SHOP_ID,
            "sum": data["sum"],
            "orderId": data["orderId"],
            "hookUrl": data.get("hookUrl", "https://example.com/hook"),
            "successUrl": data.get("successUrl", "https://example.com/success"),
            "failUrl": data.get("failUrl", "https://example.com/fail"),
            "expire": 300,
            "comment": f"Оплата от Telegram: {data['client_id']}",
            "customFields": json.dumps({"telegram_id": data["client_id"]}),
            "includeService": ["card", "sbp"]
        }

        json_data = json.dumps(payload, separators=(",", ":"))
        signature = hmac.new(SECRET_KEY.encode(), msg=json_data.encode(), digestmod=hashlib.sha256).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Signature": signature
        }

        response = requests.post(LAVA_URL, headers=headers, data=json_data.encode("utf-8"))

        try:
            lava_response = response.json()
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid JSON from Lava"}), 500

        return jsonify({
            "status": "ok",
            "lava": lava_response
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
