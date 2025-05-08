from flask import Flask, request
import requests
import sys

app = Flask(__name__)

# SignalWire credentials - use your real credentials
SIGNALWIRE_PROJECT = 'e92d48a2-3897-4817-ae34-52f1faf0b150'  # From your previous code sample
SIGNALWIRE_TOKEN = 'PT8c6bcda380b7155c0730e615ac61d048e5defc9498182091'  # From your previous code sample
SIGNALWIRE_SPACE = 'nicholas-maxwell.signalwire.com'  # From your previous code sample
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
    
    print(f"🔄 Attempting to send SMS: {message}", flush=True)
    print(f"🔗 Using URL: {url}", flush=True)
    
    try:
        response = requests.post(url, data=data, auth=auth)
        print("📤 Forwarded via SignalWire:", response.status_code, response.text, flush=True)
        return '', 204
    except Exception as e:
        print(f"❌ Error sending SMS: {e}", flush=True)
        return '', 500

@app.route('/')
def index():
    return 'Callback handler is running!'

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.form.to_dict()  # For SMS forwarding, it's expected to be form data
        print("📥 Received POST to /callback:", data, flush=True)
        # Format the message for forwarding
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
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            print("📊 Parsed JSON data:", data, flush=True)
        else:
            try:
                # Try to parse as JSON even if content-type isn't set correctly
                data = request.get_json(force=True)
                print("📊 Forced JSON parsing:", data, flush=True)
            except Exception:
                # Fall back to form data if JSON parsing fails
                data = request.form.to_dict()
                print("📊 Parsed form data:", data, flush=True)
        
        print("📩 SignalWire 10DLC webhook received:", data, flush=True)
        
        # Extract relevant fields from the webhook payload
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

if __name__ == '__main__':  # Fixed syntax error
    print("🚀 Flask with SignalWire forward logic is live", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=True)  # Added debug=True for better error reporting
