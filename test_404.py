import asyncio
from openai import AsyncOpenAI
from aiohttp import web

async def handle(request):
    return web.Response(status=404, text="404 page not found\n")

async def main():
    app = web.Application()
    app.router.add_route('*', '/{tail:.*}', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    client = AsyncOpenAI(
        base_url="http://localhost:8080",
        api_key="dummy"
    )
    try:
        await client.chat.completions.create(
            model="test",
            messages=[{"role": "user", "content": "hi"}]
        )
    except Exception as e:
        print(f"RAISED: {str(e)}")
    
    await runner.cleanup()

asyncio.run(main())
