const https = require('https');
const crypto = require('crypto');

const SECRET_KEY = 'a70c4db643d8b4b629881c7ad33bd76e5e51b26b';
const LAVA_URL = 'https://api.lava.ru/business/invoice/create';

const payload = {
  shopId: "708799d5-e970-4909-ae4e-b4f9a03ee1b4",
  sum: 1,
  orderId: "order_" + Date.now(),
  hookUrl: "https://example.com/hook",
  successUrl: "https://example.com/success",
  failUrl: "https://example.com/fail",
  expire: 300,
  comment: "Оплата от Telegram: 123456789",
  customFields: JSON.stringify({ telegram_id: "123456789" }),
  includeService: ["card", "sbp", "qiwi"]
};

const json = JSON.stringify(payload);

// Подпись (Signature)
const signature = crypto
  .createHmac('sha256', SECRET_KEY)
  .update(json)
  .digest('hex');

const options = {
  method: 'POST',
  hostname: 'api.lava.ru',
  path: '/business/invoice/create',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Signature': signature
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => (data += chunk));
  res.on('end', () => {
    try {
      const parsed = JSON.parse(data);
      console.log("Ответ от Lava:", parsed);
      if (parsed?.data?.invoice_url) {
        console.log("🔗 Ссылка на оплату:", parsed.data.invoice_url);
      } else {
        console.error("❌ Ошибка:", parsed);
      }
    } catch (err) {
      console.error("❌ Ошибка при парсинге ответа:", err);
    }
  });
});

req.on('error', (error) => {
  console.error("❌ Ошибка запроса:", error);
});

req.write(json);
req.end();
