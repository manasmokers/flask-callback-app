print("🚀 Flask with SignalWire forward logic is live")

from flask import Flask, request
import requests

app = Flask(__name__)

# SignalWire Config
SIGNALWIRE_PROJECT_ID = "e92d48a2-3897-4817-ae34-52f1faf0b150"
SIGNALWIRE_API_TOKEN = "PT8c6bcda380b7155c0730e615ac61d048e5defc9498182091"
SIGNALWIRE_SPACE_URL = "nicholas-maxwell.signalwire.com"
FROM_NUMBER = "+14085219525"
TO_NUMBER = "+16109963374"

# Shared secret to protect the endpoint
SHARED_SECRET = "mysharedsecret123"

@app.route('/callback', methods=['POST'])
def callback():
    data = request.form.to_dict()

    # 🔐 Shared secret check
    if data.get('secret') != SHARED_SECRET:
        print("❌ Unauthorized access attempt:", data)
        return 'Unauthorized', 403

    print("📥 Received POST to /callback:", data)

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
        print("📤 Forwarded via SignalWire:", response.status_code, response.text)
    except Exception as e:
        print("❌ Error forwarding:", e)

    return '', 204

@app.route('/')
def index():
    return 'Flask app is running.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


#Secure /callback with shared secret
