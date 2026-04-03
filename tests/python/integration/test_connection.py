import requests
import json

def test_fastapi_server():
    print("Testing FastAPI server...")
    base_url = "http://127.0.0.1:5000"

    # Test root endpoint
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        print(f"GET /: Success! Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"GET /: Failed! Error: {e}")

    # Test /gamestate endpoint
    test_payload = {
        "player_hand": ["C_A", "D_K"],
        "active_jokers": [{"name": "Joker", "value": 4}],
        "discard_pile": [],
        "played_cards_history": [],
        "current_score": 0,
        "current_blind_info": {"name": "Small Blind", "chips_required": 300, "reward": 10},
        "active_global_modifiers_challenges": [],
        "shop_contents": [],
        "current_stakes": 1
    }
    try:
        response = requests.post(f"{base_url}/gamestate", json=test_payload)
        response.raise_for_status()
        print(f"POST /gamestate: Success! Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"POST /gamestate: Failed! Error: {e}")

if __name__ == "__main__":
    test_fastapi_server()
