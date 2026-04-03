import unittest
import json
from unittest.mock import MagicMock
from src.python_orchestrator.rag_model.rag_processor import RAGProcessor

class TestRAGProcessor(unittest.TestCase):

    def setUp(self):
        # Mock LM Studio client as it's a dependency but not under test here
        self.mock_lm_studio_client = MagicMock()
        self.rag_processor = RAGProcessor(self.mock_lm_studio_client)

    def test_formulate_prompt(self):
        game_state = {
            "player_hand": ["AH", "KS", "QC"],
            "active_jokers": [{"name": "Joker 1", "effect": "Multiply by 2"}],
            "dollars": 100,
            "current_blind_name": "Small Blind",
            "hands_remaining": 3,
            "discards_remaining": 2
        }
        expected_prompt_part = json.dumps(game_state)
        prompt = self.rag_processor.formulate_prompt(game_state)

        self.assertIn(expected_prompt_part, prompt)
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), len(expected_prompt_part))
        self.assertIn("optimal moves for Balatro", prompt)

if __name__ == '__main__':
    unittest.main()
