from flask import Flask, request
import requests

app = Flask(__name__)

# Set these with your real SignalWire credentials
SIGNALWIRE_PROJECT_ID = "your-project-id"
SIGNALWIRE_API_TOKEN = "your-api-token"
SIGNALWIRE_SPACE_URL = "example.signalwire.com"  # without https://
TO_NUMBER = "+1YOURCELLNUMBER"
FROM_NUMBER = "+1YOURSIGNALWIRENUMBER"

@app.route('/callback', methods=['POST'])
def callback():
    data = request.form.to_dict()
    print("Received callback:", data)

    # Send SMS
    response = requests.post(
        f"https://{SIGNALWIRE_SPACE_URL}/api/laml/2010-04-01/Accounts/{SIGNALWIRE_PROJECT_ID}/Messages.json",
        auth=(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN),
        data={
            "From": FROM_NUMBER,
            "To": TO_NUMBER,
            "Body": "Test callback received!"
        }
    )
    print("SMS sent:", response.status_code, response.text)
    return '', 204