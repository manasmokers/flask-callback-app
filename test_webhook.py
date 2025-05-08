import requests
import json

# URL of your webhook endpoint
webhook_url = "https://callback-handler.waterdamagerestoration247.com/webhook"

# Mock 10DLC campaign status update payload
# This simulates what SignalWire might send when a campaign is approved
payload = {
    "campaign_id": "test_campaign_123",
    "campaign_status": "approved",
    "timestamp": "2025-05-07T12:34:56Z",
    "event_type": "campaign_status_update"
}

print("🔄 Sending test 10DLC campaign status update to webhook...")
print(f"📌 Webhook URL: {webhook_url}")
print(f"📦 Payload: {json.dumps(payload, indent=2)}")

# Send the request
try:
    # Test with JSON content type
    response = requests.post(
        webhook_url, 
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📊 Response status code: {response.status_code}")
    print(f"📄 Response body: {response.text}")
    
    if response.status_code == 204:
        print("✅ Success! The webhook returned 204 No Content as expected.")
    else:
        print("⚠️ The webhook responded, but with an unexpected status code.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("Could not connect to the webhook URL. Please check that it's accessible.")

print("\n🔍 Next steps:")
print("1. Check your Flask app logs to see if it processed the request correctly")
print("2. Verify if an SMS was sent as a result of this test request")
print("3. If no SMS was sent, check the webhook handler logic and logs")
