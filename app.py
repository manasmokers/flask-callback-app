from flask import Flask, request
import requests
import sys

app = Flask(__name__)

# Replace with your SignalWire details
SIGNALWIRE_PROJECT = 'your-project-id'
SIGNALWIRE_TOKEN = 'your-api-token'
SIGNALWIRE_SPACE = 'your-space.signalwire.com'
FROM_NUMBER = '+14085219525'
TO_NUMBER = '+16109963374'

def send_sms(message):
    try:
        print(f"📤 Attempting to send SMS: '{message}'", flush=True)
        url = f"https://{SIGNALWIRE_SPACE}/api/laml/2010-04-01/Accounts/{SIGNALWIRE_PROJECT}/Messages.json"
        payload = {
            'From': FROM_NUMBER,
            'To': TO_NUMBER,
            'Body': message
        }
        response = requests.post(url, data=payload, auth=(SIGNALWIRE_PROJECT, SIGNALWIRE_TOKEN))
        print(f"📤 SMS response {response.status_code}: {response.text}", flush=True)
        return '', 204
    except Exception as e:
        print(f"❌ Error sending SMS: {e}", file=sys.stderr, flush=True)
        return '', 500

@app.route('/')
def index():
    return '✅ Callback Handler is Running', 200

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.form.to_dict()
        print("📥 Received POST to /callback:", data, flush=True)
        body = data.get('Body')
        sender = data.get('From')
        secret = data.get('secret')

        if body and sender and secret == 'mysharedsecret123':
            return send_sms(f"[SignalWire Free Trial] Forwarded from /callback: {body} (from {sender})")
        else:
            print("⚠️ Missing fields or incorrect secret; SMS not sent", flush=True)
    except Exception as e:
        print("❌ Error in /callback:", e, file=sys.stderr, flush=True)

    return '', 204

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("🔍 Incoming webhook request content type:", request.content_type, flush=True)
        print("🔍 Raw request data:", request.get_data().decode('utf-8'), flush=True)

        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        print("📊 Parsed data:", data, flush=True)

        campaign_status = data.get('campaign_status')
        campaign_id = data.get('campaign_id', 'Unknown')
        print(f"🏷️ Extracted campaign_status: '{campaign_status}', campaign_id: '{campaign_id}'", flush=True)

        # Check for nested structures
        if not campaign_status and isinstance(data, dict):
            for key in ['data', 'payload']:
                nested = data.get(key)
                if isinstance(nested, dict):
                    campaign_status = nested.get('campaign_status')
                    campaign_id = nested.get('campaign_id', campaign_id)
                    print(f"🔍 Found nested '{key}': status={campaign_status}, id={campaign_id}", flush=True)

        if campaign_status == 'approved':
            print("✅ Campaign status is 'approved', sending SMS", flush=True)
            return send_sms(f"✅ 10DLC campaign approved: {campaign_id}")
        else:
            print(f"❓ Campaign status not 'approved': '{campaign_status}', no SMS sent", flush=True)
    except Exception as e:
        print("❌ Error in /webhook:", e, file=sys.stderr, flush=True)

    return '', 204
