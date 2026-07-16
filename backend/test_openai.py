import asyncio
from openai import AsyncOpenAI
import os

async def main():
    client = AsyncOpenAI(
        base_url="https://learning-agent-7wf9.vercel.app/v1",
        api_key="dummy-key"
    )
    try:
        completion = await client.chat.completions.create(
            model="meta/llama3-70b-instruct",
            messages=[{"role": "user", "content": "hello"}]
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")

asyncio.run(main())
