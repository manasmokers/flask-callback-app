import os
import sys
from flask import Flask, request
import requests

app = Flask(__name__)

SIGNALWIRE_SPACE_URL = os.environ.get('SIGNALWIRE_SPACE_URL')
SIGNALWIRE_PROJECT_ID = os.environ.get('SIGNALWIRE_PROJECT_ID')
SIGNALWIRE_API_TOKEN = os.environ.get('SIGNALWIRE_API_TOKEN')
SIGNALWIRE_FROM_NUMBER = os.environ.get('SIGNALWIRE_FROM_NUMBER')
FORWARD_TO_NUMBER = os.environ.get('FORWARD_TO_NUMBER')
SHARED_SECRET = os.environ.get('SHARED_SECRET')

def send_sms(message_body):
    try:
        payload = {
            "from": SIGNALWIRE_FROM_NUMBER,
            "to": FORWARD_TO_NUMBER,
            "body": f"[SignalWire Free Trial] {message_body}"
        }

        response = requests.post(
            f"https://{SIGNALWIRE_SPACE_URL}/api/laml/2010-04-01/Accounts/{SIGNALWIRE_PROJECT_ID}/Messages.json",
            auth=(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN),
            data=payload
        )

        print("📤 Forwarded via SignalWire:", response.status_code, response.text, flush=True)
        return '', 204
    except Exception as e:
        print("❌ Error sending SMS:", e, file=sys.stderr, flush=True)
        return '', 500

@app.route('/', methods=['GET'])
def health_check():
    return '✅ Flask is running\n', 200

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.form.to_dict()
        print("📥 Received POST to /callback:", data, flush=True)

        secret = data.get("secret")
        if secret != SHARED_SECRET:
            print("⚠️ Invalid secret provided", flush=True)
            return '', 403

        body = data.get("Body", "")
        sender = data.get("From", "Unknown")
        return send_sms(f"Forwarded from /callback: {body} (from {sender})")
    except Exception as e:
        print("❌ Error in /callback:", e, file=sys.stderr, flush=True)
        return '', 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("🔍 Incoming webhook request content type:", request.content_type, flush=True)
        print("🔍 Request data:", request.get_data().decode('utf-8'), flush=True)

        if request.is_json:
            data = request.get_json()
            print("📊 Parsed JSON data:", data, flush=True)
        else:
            data = request.form.to_dict()
            print("📊 Parsed form data:", data, flush=True)

        print("📩 SignalWire 10DLC webhook received:", data, flush=True)

        campaign_status = data.get('campaign_status')
        campaign_id = data.get('campaign_id', 'Unknown')
        print(f"🏷️ Extracted campaign_status: '{campaign_status}', campaign_id: '{campaign_id}'", flush=True)

        if not campaign_status and isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], dict):
                nested_data = data['data']
                campaign_status = nested_data.get('campaign_status')
                campaign_id = nested_data.get('campaign_id', campaign_id)
                print(f"🔍 Found nested data. New status: '{campaign_status}', id: '{campaign_id}'", flush=True)
            elif 'payload' in data and isinstance(data['payload'], dict):
                nested_data = data['payload']
                campaign_status = nested_data.get('campaign_status')
                campaign_id = nested_data.get('campaign_id', campaign_id)
                print(f"🔍 Found payload data. New status: '{campaign_status}', id: '{campaign_id}'", flush=True)

        if campaign_status == 'approved':
            print("✅ Campaign status is 'approved', sending SMS", flush=True)
            return send_sms(f"✅ 10DLC campaign approved: {campaign_id}")
        else:
            print(f"❓ Campaign status is not 'approved' (actual value: '{campaign_status}'), SMS not sent", flush=True)
    except Exception as e:
        print("❌ Error in /webhook:", e, file=sys.stderr, flush=True)

    return '', 204
