
import httpx
import asyncio
import time

url = "http://127.0.0.1:8006/aio2"

async def aio_req_test(client: httpx.AsyncClient, semaphore: asyncio.Semaphore):
    async with semaphore:
        response = await client.get(url)
        print(time.strftime("%Y-%m-%d %H:%M:%S"), response.text)

async def main():
    CONCURRENCY_LIMIT = 100  # 提高并发限制

    # 在 async 函数内部创建异步对象，确保它们属于同一个事件循环
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    limits = httpx.Limits(max_connections=CONCURRENCY_LIMIT, max_keepalive_connections=CONCURRENCY_LIMIT)

    # 使用 async with 来自动管理客户端的生命周期（连接和关闭）
    async with httpx.AsyncClient( limits=limits, timeout=30.0) as client:
        tasks = [aio_req_test(client, semaphore) for _ in range(5000)]
        await asyncio.gather(*tasks)

asyncio.run(main())
