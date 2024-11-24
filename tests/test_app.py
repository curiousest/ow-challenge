import os
import time
import unittest
from unittest.mock import MagicMock, patch

import requests
from fastapi.testclient import TestClient

from src.app import app, get_report_with_backoff

# Create a test client for the FastAPI app
client = TestClient(app)

mocked_messages = {
    "messages": [
        {
            "text": "Generate a Tenant Obligations Report for the new lease terms.",
            "timestamp": "2024-04-29T02:08:29.375Z",
            "report_id": 5392,
            "id": 1000
        },
        {
            "text": "Are there any restrictions on alterations or improvements?",
            "timestamp": "2024-04-29T03:25:03.613Z",
            "id": 1001
        },
        {
            "text": "Is there a clause for default and remedies?",
            "timestamp": "2024-04-29T07:27:34.985Z",
            "id": 1002
        },
        {
            "text": "What are the indemnity provisions?",
            "timestamp": "2024-04-29T10:22:13.926Z",
            "id": 1003
        },
        {
            "text": "What is the security deposit amount?",
            "timestamp": "2024-04-29T11:54:18.493Z",
            "id": 1004
        }
    ]
}


class TestFastAPIEndpoints(unittest.TestCase):
    @patch("src.app.get_report_with_backoff", return_value=None)
    @patch("requests.get")
    def test_calculate_credits_pytorch_endpoint(self, mock_get_report, mock_get):
        # Mock the requests.get for messages endpoint
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=mocked_messages))

        # Set environment variable to PyTorch for testing
        os.environ["CREDIT_CALCULATION_METHOD"] = "pytorch"
        response = client.get("/usage")
        self.assertEqual(response.status_code, 200)
        self.assertIn("usage", response.json())

    @patch("src.app.get_report_with_backoff", return_value=None)
    @patch("requests.get")
    def test_calculate_credits_pandas_endpoint(self, mock_get_report, mock_get):
        # Mock the requests.get for messages endpoint
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=mocked_messages))

        # Set environment variable to Pandas for testing
        os.environ["CREDIT_CALCULATION_METHOD"] = "pandas"
        response = client.get("/usage")
        self.assertEqual(response.status_code, 200)
        self.assertIn("usage", response.json())
    
    @patch("requests.get")
    @patch("src.app.get_report_with_backoff")
    def test_calculate_credits_with_report_hit(self, mock_get_report, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=mocked_messages))

        def none_generator():
            yield {"name": "Initial Report", "credit_cost": 100.0}  # First call returns a value
            while True:
                yield None  # Subsequent calls return None

        # Set the side effect for get_report_with_backoff to use the generator
        mock_get_report.side_effect = none_generator()

        # Set environment variable to PyTorch for testing
        os.environ["CREDIT_CALCULATION_METHOD"] = "pytorch"
        response = client.get("/usage")
        self.assertEqual(response.status_code, 200)
        self.assertIn("usage", response.json())
        self.assertEqual(response.json()["usage"][0]["report_name"], "Initial Report")

    @patch("requests.get")
    def test_exponential_backoff(self, mock_get):
        # Mock the requests.get to always return a non-200 status code
        mock_get.return_value = MagicMock(status_code=500)
        report_id = 1234
        start_time = time.time()
        get_report_with_backoff(report_id, max_retries=3, backoff_time=0.01)
        end_time = time.time()

        # The backoff times should be 0.01 + 0.02 + 0.04 = 0.07 seconds
        expected_minimum_duration = 0.07
        self.assertGreaterEqual(end_time - start_time, expected_minimum_duration)
