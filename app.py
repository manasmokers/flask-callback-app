from flask import Flask, request
import requests
import sys

app = Flask(__name__)

# Replace with your actual SignalWire credentials and numbers
SIGNALWIRE_PROJECT = 'your-project-id'
SIGNALWIRE_TOKEN = 'your-api-token'
SIGNALWIRE_SPACE = 'your-space.signalwire.com'
FROM_NUMBER = '+14085219525'
TO_NUMBER = '+16109963374'

def send_sms(message):
    url = f"https://{SIGNALWIRE_SPACE}/api/laml/2010-04-01/Accounts/{SIGNALWIRE_PROJECT}/Messages.json"
    auth = (SIGNALWIRE_PROJECT, SIGNALWIRE_TOKEN)
    data = {
        'From': FROM_NUMBER,
        'To': TO_NUMBER,
        'Body': message
    }
    response = requests.post(url, data=data, auth=auth)
    print("📤 Forwarded via SignalWire:", response.status_code, response.text, flush=True)
    return '', 204

@app.route('/')
def index():
    return 'Callback handler is running!'

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.form.to_dict()
        print("📥 Received POST to /callback:", data, flush=True)

        message = f"[SignalWire Free Trial] Forwarded from /callback: {data.get('Body', '')} (from {data.get('From', '')})"
        return send_sms(message)

    except Exception as e:
        print("❌ Error in /callback:", e, file=sys.stderr, flush=True)
        return '', 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("🔍 Incoming webhook request content type:", request.content_type, flush=True)
        raw_data = request.get_data(as_text=True)
        print("🔍 Raw request data:", raw_data, flush=True)

        try:
            data = request.get_json(force=True)
            print("📊 Parsed JSON data:", data, flush=True)
        except Exception as json_err:
            print("⚠️ Failed to parse JSON, falling back to form data:", json_err, flush=True)
            data = request.form.to_dict()
            print("📊 Parsed form data:", data, flush=True)

        print("📩 SignalWire 10DLC webhook received:", data, flush=True)

        campaign_status = data.get('campaign_status')
        campaign_id = data.get('campaign_id', 'Unknown')

        print(f"🏷️ Extracted campaign_status: '{campaign_status}', campaign_id: '{campaign_id}'", flush=True)

        if campaign_status == 'approved':
            print("✅ Campaign status is 'approved', sending SMS", flush=True)
            return send_sms(f"✅ 10DLC campaign approved: {campaign_id}")
        else:
            print(f"❓ Campaign status is not 'approved' (actual value: '{campaign_status}'), SMS not sent", flush=True)

    except Exception as e:
        print("❌ Error in /webhook:", e, file=sys.stderr, flush=True)

    return '', 204

if __name__ == '__main__':
    print("🚀 Flask with SignalWire forward logic is live", flush=True)
    app.run(host='0.0.0.0', port=5000)
