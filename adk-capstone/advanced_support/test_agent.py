import requests
import json
import time

def test_agent():
    # Fetch agent card to find the endpoint
    card_url = "http://localhost:8005/.well-known/agent-card"
    print(f"Fetching agent card from {card_url}...")
    try:
        card_resp = requests.get(card_url)
        print(f"Card Status: {card_resp.status_code}")
        if card_resp.status_code != 200:
            print(f"Failed to fetch card: {card_resp.text}")
            return
        
        card_data = card_resp.json()
        print(f"Card Data: {json.dumps(card_data, indent=2)}")
        
        # Look for a chat interface or similar
        # ADK usually exposes interfaces. If not explicitly listed, we might have to guess based on the card.
        # But let's see the card first.
        
        # For now, let's try to infer the endpoint or just print the card and stop.
        # But if we want to proceed, we can try /agent/chat if it exists in the card?
        
    except Exception as e:
        print(f"Error fetching card: {e}")
        return

if __name__ == "__main__":
    # Wait a bit for server to start
    time.sleep(2)
    test_agent()
