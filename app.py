print("🚀 Flask base app is live")

from flask import Flask, request
import sys

app = Flask(__name__)

@app.route('/')
def index():
    print("✅ Root / route was hit", flush=True)
    return 'Flask app is running.', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    print("🔔 /webhook route was hit", flush=True)
    print("📩 Payload:", request.form.to_dict(), flush=True)
    return 'Webhook received.', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
