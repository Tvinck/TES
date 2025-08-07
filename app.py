from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import requests

app = Flask(__name__)

# 🔐 Секретный ключ и Shop ID из твоей Lava Business панели
SECRET_KEY = 'a70c4db643d8b4b629881c7ad33bd76e5e51b26b'
SHOP_ID = '708799d5-e970-4909-ae4e-b4f9a03ee1b4'
LAVA_URL = 'https://api.lava.ru/business/invoice/create'

@app.route('/pay', methods=['POST'])
def pay():
    try:
        data = request.get_json()

        # Валидация и безопасное извлечение данных
        amount = float(data.get("sum"))
        order_id = str(data.get("orderId"))
        client_id = str(data.get("client_id"))

        # Формируем тело запроса в Lava
        payload = {
            "shopId": SHOP_ID,
            "sum": amount,
            "orderId": order_id,
            "hookUrl": "https://example.com/hook",
            "successUrl": "https://example.com/success",
            "failUrl": "https://example.com/fail",
            "expire": 300,
            "comment": f"Оплата от Telegram: {client_id}",
            "customFields": json.dumps({ "telegram_id": client_id }),
            "includeService": ["card", "sbp", "qiwi"]
        }

        json_payload = json.dumps(payload, separators=(',', ':'))  # важно: без пробелов

        # Генерация подписи
        signature = hmac.new(
            key=SECRET_KEY.encode(),
            msg=json_payload.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Запрос в Lava
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Signature": signature
        }

        lava_response = requests.post(LAVA_URL, data=json_payload, headers=headers)
        lava_data = lava_response.json()

        # Возврат ответа клиенту
        return jsonify({
            "status": "ok",
            "lava": lava_data
        })

    except Exception as e:
        return jsonify({
            "статус": "ошибка",
            "ошибка": str(e)
        }), 500
