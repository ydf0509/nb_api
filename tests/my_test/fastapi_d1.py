from auto_run_on_remote import run_current_script_on_remote

run_current_script_on_remote()


from nb_api.contrib.fastapi_helpers import set_anyio_thread_limiter_total_tokens
import os



import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from fastapi import FastAPI
import uvicorn
import starlette

from contextlib import asynccontextmanager
import anyio
from anyio import to_thread



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时设置线程池大小
    DEFAULT_THREAD_POOL_WORKERS = 300
    set_anyio_thread_limiter_total_tokens(DEFAULT_THREAD_POOL_WORKERS)
    # to_thread.current_default_thread_limiter().total_tokens = DEFAULT_THREAD_POOL_WORKERS
    print(f"Thread pool size set to: {DEFAULT_THREAD_POOL_WORKERS}")
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Root"])
def read_root():
    # 这个 time.sleep(1) 会在上面创建的线程池中的某个线程里执行
    time.sleep(1)
    return {"message": "欢迎来到 fastapi-d1 示例 API!"}


@app.get("/aio2", tags=["Root"])
async def aio_api():
    # await asyncio.sleep(1)
    return {"message": "欢迎来到aio1 示例 API!"}


if __name__ == "__main__":
    # 使用 uvicorn 启动应用
    uvicorn.run('fastapi_d1:app', host="0.0.0.0", port=8006)