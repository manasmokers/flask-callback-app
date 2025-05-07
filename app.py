from flask import Flask, request
import requests
import sys
import os

app = Flask(__name__)

SIGNALWIRE_PROJECT_ID = os.environ.get("SIGNALWIRE_PROJECT_ID", "your-project-id")
SIGNALWIRE_API_TOKEN = os.environ.get("SIGNALWIRE_API_TOKEN", "your-api-token")
SIGNALWIRE_SPACE = os.environ.get("SIGNALWIRE_SPACE", "your-space.signalwire.com")
FORWARD_TO_NUMBER = os.environ.get("FORWARD_TO_NUMBER", "+16109963374")
FORWARD_FROM_NUMBER = os.environ.get("FORWARD_FROM_NUMBER", "+14085219525")
SHARED_SECRET = os.environ.get("SHARED_SECRET", "mysharedsecret123")

def send_sms(body):
    url = f"https://{SIGNALWIRE_SPACE}/api/laml/2010-04-01/Accounts/{SIGNALWIRE_PROJECT_ID}/Messages.json"
    payload = {
        "From": FORWARD_FROM_NUMBER,
        "To": FORWARD_TO_NUMBER,
        "Body": body
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    print(f"📤 Sending SMS via SignalWire: {payload}", flush=True)
    response = requests.post(url, data=payload, auth=(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN), headers=headers)
    print(f"📬 Response from SignalWire: {response.status_code} {response.text}", flush=True)
    return '', 204

@app.route("/")
def index():
    return "✅ Callback server is live"

@app.route("/callback", methods=["POST"])
def callback():
    try:
        data = request.form.to_dict()
        print(f"📥 Received POST to /callback: {data}", flush=True)

        if data.get("secret") != SHARED_SECRET:
            print("🔒 Unauthorized: Invalid secret", flush=True)
            return "Unauthorized", 403

        body = data.get("Body", "")
        sender = data.get("From", "Unknown")
        message = f"[SignalWire Free Trial] Forwarded from /callback: {body} (from {sender})"
        return send_sms(message)
    except Exception as e:
        print("❌ Error in /callback:", e, file=sys.stderr, flush=True)
        return "Error", 500

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
