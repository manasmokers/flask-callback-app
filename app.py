print("🚀 Flask with SignalWire forward logic is live")

from flask import Flask, request
import requests
import sys

app = Flask(__name__)

# SignalWire Config
SIGNALWIRE_PROJECT_ID = "e92d48a2-3897-4817-ae34-52f1faf0b150"
SIGNALWIRE_API_TOKEN = "PT8c6bcda380b7155c0730e615ac61d048e5defc9498182091"
SIGNALWIRE_SPACE_URL = "nicholas-maxwell.signalwire.com"
FROM_NUMBER = "+14085219525"
TO_NUMBER = "+16109963374"

# Shared secret to protect the secure endpoint
SHARED_SECRET = "mysharedsecret123"

@app.route('/')
def index():
    return 'Flask app is running.'

@app.route('/callback', methods=['POST'])
def callback():
    data = request.form.to_dict()

    # 🔐 Shared secret check
    if data.get('secret') != SHARED_SECRET:
        print("❌ Unauthorized access attempt:", data, file=sys.stderr, flush=True)
        return 'Unauthorized', 403

    print("📥 Received POST to /callback:", data, flush=True)

    body = data.get('Body', 'No body provided')
    sender = data.get('From', 'Unknown')

    try:
        response = requests.post(
            f"https://{SIGNALWIRE_SPACE_URL}/api/laml/2010-04-01/Accounts/{SIGNALWIRE_PROJECT_ID}/Messages.json",
            auth=(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN),
            data={
                "From": FROM_NUMBER,
                "To": TO_NUMBER,
                "Body": f"Forwarded from /callback: {body} (from {sender})"
            }
        )
        print("📤 Forwarded via SignalWire:", response.status_code, response.text, flush=True)
    except Exception as e:
        print("❌ Error forwarding:", e, file=sys.stderr, flush=True)

    return '', 204

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.form.to_dict()
    print("📩 SignalWire 10DLC webhook received:", data, flush=True)

    # Optional SMS notification
    try:
        status = data.get('campaign_status')
        campaign_id = data.get('campaign_id')

        if status and campaign_id:
            sms_body = f"10DLC Update: Campaign {campaign_id} is now '{status}'"
            response = requests.post(
                f"https://{SIGNALWIRE_SPACE_URL}/api/laml/2010-04-01/Accounts/{SIGNALWIRE_PROJECT_ID}/Messages.json",
                auth=(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN),
                data={
                    "From": FROM_NUMBER,
                    "To": TO_NUMBER,
                    "Body": sms_body
                }
            )
            print("📤 Webhook SMS sent:", response.status_code, response.text, flush=True)
    except Exception as e:
        print("❌ Webhook SMS error:", e, file=sys.stderr, flush=True)

    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
