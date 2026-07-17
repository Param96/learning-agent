import asyncio
from openai import AsyncOpenAI
import httpx

# create a dummy transport to capture the URL
class MockTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        print(f"URL CALLED: {request.url}")
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

async def main():
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1/chat/completions",
        api_key="dummy-key",
        http_client=httpx.AsyncClient(transport=MockTransport())
    )
    await client.chat.completions.create(
        model="test",
        messages=[{"role": "user", "content": "hi"}]
    )

asyncio.run(main())
