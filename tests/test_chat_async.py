import unittest.mock as mock

import pytest
from mitta_mistralai.async_client import MistralAsyncClient
from mitta_mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatMessage,
)

from .utils import (
    mock_async_stream_response,
    mock_chat_response_payload,
    mock_chat_response_streaming_payload,
    mock_response,
)


@pytest.fixture()
def client():
    client = MistralAsyncClient()
    client._client = mock.AsyncMock()
    client._client.stream = mock.Mock()
    return client


class TestAsyncChat:
    @pytest.mark.asyncio
    async def test_chat(self, client):
        client._client.request.return_value = mock_response(
            200,
            mock_chat_response_payload(),
        )

        result = await client.chat(
            model="mistral-small",
            messages=[
                ChatMessage(role="user", content="What is the best French cheese?")
            ],
        )

        client._client.request.assert_awaited_once_with(
            "post",
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "User-Agent": f"mistral-client-python/{client._version}",
                "Accept": "application/json",
                "Authorization": "Bearer None",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistral-small",
                "messages": [
                    {"role": "user", "content": "What is the best French cheese?"}
                ],
                "safe_prompt": False,
                "stream": False,
            },
        )

        assert isinstance(
            result, ChatCompletionResponse
        ), "Should return an ChatCompletionResponse"
        assert len(result.choices) == 1
        assert result.choices[0].index == 0
        assert result.object == "chat.completion"

    @pytest.mark.asyncio
    async def test_chat_streaming(self, client):
        client._client.stream.return_value = mock_async_stream_response(
            200,
            mock_chat_response_streaming_payload(),
        )

        result = client.chat_stream(
            model="mistral-small",
            messages=[
                ChatMessage(role="user", content="What is the best French cheese?")
            ],
        )

        results = [r async for r in result]

        client._client.stream.assert_called_once_with(
            "post",
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Accept": "text/event-stream",
                "User-Agent": f"mistral-client-python/{client._version}",
                "Authorization": "Bearer None",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistral-small",
                "messages": [
                    {"role": "user", "content": "What is the best French cheese?"}
                ],
                "safe_prompt": False,
                "stream": True,
            },
        )

        for i, result in enumerate(results):
            if i == 0:
                assert isinstance(
                    result, ChatCompletionStreamResponse
                ), "Should return an ChatCompletionStreamResponse"
                assert len(result.choices) == 1
                assert result.choices[0].index == 0
                assert result.choices[0].delta.role == "assistant"
            else:
                assert isinstance(
                    result, ChatCompletionStreamResponse
                ), "Should return an ChatCompletionStreamResponse"
                assert len(result.choices) == 1
                assert result.choices[0].index == i - 1
                assert result.choices[0].delta.content == f"stream response {i-1}"
                assert result.object == "chat.completion.chunk"
