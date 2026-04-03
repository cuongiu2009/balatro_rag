import unittest
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock, patch
from src.python_orchestrator.communication.socket_server import handle_game_state, lm_studio_client, rag_processor

class TestAISuggestionPipeline(unittest.TestCase):

import unittest
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock, patch
# Import the actual module containing handle_game_state
from src.python_orchestrator.communication.socket_server import handle_game_state, lm_studio_client, rag_processor

class TestAISuggestionPipeline(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Reset mocks before each test
        # lm_studio_client.get_suggestion will be mocked directly to return parsed data
        lm_studio_client.get_suggestion = MagicMock()
        rag_processor.formulate_prompt = MagicMock()
        # rag_processor.parse_lm_studio_response is no longer part of the pipeline here
        # so no need to mock it.

        # Define a sample game state
        self.sample_game_state = {
            "player_hand": ["AH", "KS", "QC"],
            "active_jokers": [{"name": "Joker 1", "effect": "Multiply by 2"}],
            "dollars": 100,
            "hands_remaining": 3,
            "discards_remaining": 2,
            "current_blind_name": "Small Blind",
            "debug_path_log": []
        }

        # Define a mock parsed suggestion (this is what lm_studio_client.get_suggestion should return)
        self.mock_parsed_suggestion = {
            "action": "Play",
            "card_ids": ["AH", "AD", "AC", "AS"],
            "location_indices": [1, 2, 3, 4],
            "estimated_score": 500,
            "win_chance": 75.5,
            "rationale": "Four of a kind is a strong hand."
        }

    def test_handle_game_state_success(self):
        # Configure mocks
        rag_processor.formulate_prompt.return_value = "Mocked prompt"
        # lm_studio_client.get_suggestion now returns the parsed suggestion directly
        lm_studio_client.get_suggestion.return_value = self.mock_parsed_suggestion

        # Run the async function
        response = asyncio.run(handle_game_state(self.sample_game_state))

        # Assertions
        rag_processor.formulate_prompt.assert_called_once_with(self.sample_game_state)
        lm_studio_client.get_suggestion.assert_called_once_with("Mocked prompt")
        # No call to rag_processor.parse_lm_studio_response is expected anymore

        self.assertIsInstance(response, dict)
        self.assertEqual(response.get("status"), "success")
        self.assertDictEqual(response.get("data"), self.mock_parsed_suggestion)
        
    def test_handle_game_state_lm_studio_failure(self):
        # Configure mocks for LM Studio failure
        rag_processor.formulate_prompt.return_value = "Mocked prompt"
        lm_studio_client.get_suggestion.return_value = None # Simulate failure to get a valid, parsed suggestion
        
        response = asyncio.run(handle_game_state(self.sample_game_state))
        
        self.assertEqual(response.get("status"), "error")
        # Updated message as per socket_server.py
        self.assertIn("Failed to get valid suggestion from AI", response.get("message"))
        rag_processor.formulate_prompt.assert_called_once_with(self.sample_game_state)
        lm_studio_client.get_suggestion.assert_called_once_with("Mocked prompt")
        # No call to rag_processor.parse_lm_studio_response is expected

    def test_handle_game_state_lm_studio_malformed_response_handled_internally(self):
        # Simulate LM Studio client handling malformed response and returning None
        rag_processor.formulate_prompt.return_value = "Mocked prompt"
        lm_studio_client.get_suggestion.return_value = None # Client returns None if it fails to parse/validate
        
        response = asyncio.run(handle_game_state(self.sample_game_state))
        
        self.assertEqual(response.get("status"), "error")
        # Updated message as per socket_server.py
        self.assertIn("Failed to get valid suggestion from AI", response.get("message"))
        rag_processor.formulate_prompt.assert_called_once_with(self.sample_game_state)
        lm_studio_client.get_suggestion.assert_called_once_with("Mocked prompt")
        # No call to rag_processor.parse_lm_studio_response is expected

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
