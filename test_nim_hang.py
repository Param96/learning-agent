import asyncio
from openai import AsyncOpenAI
import time

async def main():
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="dummy-key"
    )
    start = time.time()
    try:
        completion = await client.chat.completions.create(
            model="llama",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=10
        )
        print("Success:", completion)
    except Exception as e:
        print(f"Failed in {time.time() - start:.2f}s with error: {e}")

asyncio.run(main())
