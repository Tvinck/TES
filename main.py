from flask import Flask, request, jsonify
import hashlib
import hmac
import json

app = Flask(__name__)

SECRET_KEY = "a70c4db643d8b4b629881c7ad33bd76e5e51b26b"

@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    payload = request.get_json()
    raw = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return jsonify({
        "status": "ok",
        "signature": signature,
        "raw": raw
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
