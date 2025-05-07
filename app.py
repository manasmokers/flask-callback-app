from flask import Flask, request
import requests

app = Flask(__name__)

# --- SignalWire Configuration ---
SIGNALWIRE_PROJECT_ID = "e92d48a2-3897-4817-ae34-52f1faf0b150"
SIGNALWIRE_API_TOKEN = "PT8c6bcda380b7155c0730e615ac61d048e5defc9498182091"
SIGNALWIRE_SPACE_URL = "nicholas-maxwell.signalwire.com"
FROM_NUMBER = "+14085219525"  # your SignalWire number
TO_NUMBER = "+16109963374"    # your personal cell

@app.route('/callback', methods=['POST'])
def callback():
    data = request.form.to_dict()
    print("📥 Received POST to /callback:", data)

    body = data.get('Body', 'No message body provided')
    sender = data.get('From', 'Unknown sender')

    # Send SMS via SignalWire
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
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

