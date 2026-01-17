import pytest
from unittest.mock import patch


class TestClientFactory:
    def test_returns_gemini_client_for_gemini_model(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            from src.clients.factory import get_client
            from src.clients.gemini import GeminiClient

            client = get_client("gemini-2.0-flash")

            assert isinstance(client, GeminiClient)

    def test_returns_openai_client_for_gpt_model(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.clients.factory import get_client
            from src.clients.openai import OpenAIClient

            client = get_client("gpt-4o-mini")

            assert isinstance(client, OpenAIClient)

    def test_returns_openai_client_for_o1_model(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.clients.factory import get_client
            from src.clients.openai import OpenAIClient

            client = get_client("o1-preview")

            assert isinstance(client, OpenAIClient)

    def test_returns_openai_client_for_unknown_model(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.clients.factory import get_client
            from src.clients.openai import OpenAIClient

            client = get_client("some-other-model")

            assert isinstance(client, OpenAIClient)

    def test_gemini_client_uses_provided_model(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            from src.clients.factory import get_client

            client = get_client("gemini-2.5-pro")

            assert client.default_model == "gemini-2.5-pro"

    def test_openai_client_uses_provided_model(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.clients.factory import get_client

            client = get_client("gpt-4o")

            assert client.default_model == "gpt-4o"
