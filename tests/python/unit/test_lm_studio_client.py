import unittest
import json
from unittest.mock import patch, MagicMock
from src.python_orchestrator.api_client.lm_studio_client import LMStudioClient
import requests

class TestLMStudioClient(unittest.TestCase):

    def setUp(self):
        self.lm_client = LMStudioClient(base_url="http://localhost:1234/v1")
        self.prompt = "What's the best play?"
        self.mock_suggestion_data = {
            "action": "Play",
            "card_ids": ["2H", "3H", "4H", "5H", "6H"],
            "location_indices": [1, 2, 3, 4, 5],
            "estimated_score": 1000,
            "win_chance": 85,
            "rationale": "A flush is a strong hand."
        }
        self.mock_system_message = "You are a helpful Balatro assistant. Your responses should be formatted as a JSON object strictly following the Suggestion JSON Schema: {'action': 'Play', 'card_ids': ['CS', 'DS', 'HS', 'SS', '2C'], 'location_indices': [1,2,3,4,5], 'estimated_score': 1234, 'win_chance': 95, 'rationale': 'This forms a flush.'}"

    @patch('requests.get')
    def test_check_connection_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "model1"}]}
        mock_get.return_value = mock_response

        result = self.lm_client.check_connection()
        self.assertTrue(result)
        mock_get.assert_called_once_with(f"{self.lm_client.base_url}/models")

    @patch('requests.get')
    def test_check_connection_failure_status_code(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        result = self.lm_client.check_connection()
        self.assertFalse(result)
        mock_get.assert_called_once_with(f"{self.lm_client.base_url}/models")

    @patch('requests.get', side_effect=requests.exceptions.RequestException("Connection Error"))
    def test_check_connection_failure_exception(self, mock_get):
        result = self.lm_client.check_connection()
        self.assertFalse(result)
        mock_get.assert_called_once_with(f"{self.lm_client.base_url}/models")

    @patch('requests.post')
    @patch('src.python_orchestrator.api_client.lm_studio_client.LMStudioClient.check_connection', return_value=True)
    def test_get_suggestion_success(self, mock_check_connection, mock_post):
        mock_response_content = json.dumps(self.mock_suggestion_data)
        mock_api_response = {
            "choices": [{
                "message": {"content": mock_response_content}
            }]
        }

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = mock_api_response
        mock_post_response.raise_for_status.return_value = None # Ensure no exception is raised
        mock_post.return_value = mock_post_response

        result = self.lm_client.get_suggestion(self.prompt)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertDictEqual(result, self.mock_suggestion_data)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("json", kwargs)
        self.assertEqual(kwargs["json"]["messages"][0]["content"], self.mock_system_message)
        self.assertEqual(kwargs["json"]["messages"][1]["content"], self.prompt)
        self.assertEqual(kwargs["json"]["response_format"], {"type": "json_object"})

    @patch('requests.post')
    @patch('src.python_orchestrator.api_client.lm_studio_client.LMStudioClient.check_connection', return_value=True)
    def test_get_suggestion_malformed_json_content(self, mock_check_connection, mock_post):
        mock_api_response = {
            "choices": [{
                "message": {"content": "{invalid json}"}
            }]
        }

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = mock_api_response
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response

        result = self.lm_client.get_suggestion(self.prompt)

        self.assertIsNone(result)
        mock_post.assert_called_once()

    @patch('requests.post')
    @patch('src.python_orchestrator.api_client.lm_studio_client.LMStudioClient.check_connection', return_value=True)
    def test_get_suggestion_missing_required_fields(self, mock_check_connection, mock_post):
        incomplete_suggestion_data = {
            "action": "Play",
            "card_ids": ["2H"]
            # Missing location_indices, estimated_score, win_chance
        }
        mock_response_content = json.dumps(incomplete_suggestion_data)
        mock_api_response = {
            "choices": [{
                "message": {"content": mock_response_content}
            }]
        }

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = mock_api_response
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response

        result = self.lm_client.get_suggestion(self.prompt)

        self.assertIsNone(result)
        mock_post.assert_called_once()

    @patch('requests.post', side_effect=requests.exceptions.RequestException("API Error"))
    @patch('src.python_orchestrator.api_client.lm_studio_client.LMStudioClient.check_connection', return_value=True)
    def test_get_suggestion_api_exception(self, mock_check_connection, mock_post):
        result = self.lm_client.get_suggestion(self.prompt)
        self.assertIsNone(result)
        mock_post.assert_called_once()

    @patch('requests.post')
    @patch('src.python_orchestrator.api_client.lm_studio_client.LMStudioClient.check_connection', return_value=False)
    def test_get_suggestion_no_connection(self, mock_check_connection, mock_post):
        result = self.lm_client.get_suggestion(self.prompt)
        self.assertIsNone(result)
        mock_check_connection.assert_called_once()
        mock_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
