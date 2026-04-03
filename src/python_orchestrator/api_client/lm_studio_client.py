import requests
import logging
import json # Added this import

class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234/v1"):
        self.base_url = base_url
        logging.info(f"LM Studio Client initialized for base URL: {self.base_url}")

    def check_connection(self):
        try:
            # A simple way to check connection is to list the models
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                logging.info("Successfully connected to LM Studio API.")
                logging.info(f"Available models: {response.json()}")
                return True
            else:
                logging.error(f"Failed to connect to LM Studio. Status: {response.status_code}, Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to LM Studio API: {e}")
            return False

    def get_suggestion(self, prompt, model="gemma-3-4b-it-Q4_K_M.gguf"):
        """
        Sends a prompt to the LM Studio API and attempts to parse the response
        into the structured suggestion format (Suggestion JSON Schema).
        Handles malformed responses by logging errors and returning None.
        """
        if not self.check_connection():
            return None

        headers = {"Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful Balatro assistant. Your responses should be formatted as a JSON object strictly following the Suggestion JSON Schema: {'action': 'Play', 'card_ids': ['CS', 'DS', 'HS', 'SS', '2C'], 'location_indices': [1,2,3,4,5], 'estimated_score': 1234, 'win_chance': 95, 'rationale': 'This forms a flush.'}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,

        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            lm_response_json = response.json()

            # Extract the content from the LM Studio response
            if 'choices' in lm_response_json and len(lm_response_json['choices']) > 0:
                message_content = lm_response_json['choices'][0]['message']['content']
                # Check and strip markdown code block if present
                if message_content.strip().startswith("```json") and message_content.strip().endswith("```"):
                    # Remove '```json' from start and '```' from end
                    message_content = message_content.strip()[len("```json"):].strip()
                    if message_content.endswith("```"):
                        message_content = message_content[:-len("```")].strip()
                try:
                    # Attempt to parse the message content as JSON
                    suggestion_data = json.loads(message_content)

                    # Validate against the Suggestion JSON Schema (basic validation)
                    required_fields = ["action", "card_ids", "location_indices", "estimated_score", "win_chance"]
                    if not all(field in suggestion_data for field in required_fields):
                        logging.error(f"LM Studio response is missing required fields. Response: {message_content}")
                        return None
                    # Further type checking can be added here if needed, but for now,
                    # just checking for existence is enough for "robust error handling for malformed responses"
                    # as per the task description.

                    return suggestion_data

                except json.JSONDecodeError as e:
                    logging.error(f"LM Studio returned malformed JSON: {e}. Raw content: {message_content}")
                    return None
                except Exception as e:
                    logging.error(f"Error processing LM Studio response content: {e}. Raw content: {message_content}")
                    return None
            else:
                logging.error(f"LM Studio response does not contain expected 'choices' or 'message' field. Full response: {lm_response_json}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting suggestion from LM Studio: {e}")
            return None

# Example usage:
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    lm_client = LMStudioClient()
    if lm_client.check_connection():
        # This is a dummy prompt for testing purposes.
        # The prompt should ideally guide the model to return the JSON format.
        dummy_prompt = "My hand is [AH, KH, QH, JH, 10H]. What should I do? Please respond with a JSON object containing 'action', 'card_ids', 'location_indices', 'estimated_score', 'win_chance', and optionally 'rationale'. For example: {'action': 'Play', 'card_ids': ['AH', 'KH', 'QH', 'JH', '10H'], 'location_indices': [1,2,3,4,5], 'estimated_score': 1000, 'win_chance': 80, 'rationale': 'You have a Royal Flush.'}"
        suggestion = lm_client.get_suggestion(dummy_prompt)
        if suggestion:
            print("Received parsed suggestion from LM Studio:")
            print(json.dumps(suggestion, indent=2))
        else:
            print("Failed to get a valid suggestion.")
