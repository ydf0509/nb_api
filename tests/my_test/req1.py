
import httpx
from concurrent.futures import ThreadPoolExecutor
import time

url = "http://127.0.0.1:8006/aio2"
pool = ThreadPoolExecutor(max_workers=500)

client = httpx.Client(
    limits=httpx.Limits(
        max_connections=1000,      # 最大 TCP 连接数
        max_keepalive_connections=1000  # 最大 keep-alive 连接数
    ),
    timeout=30.0  # 超时时间
)

def req_test():
    response = client.get(url)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),response.text)

for i in range(5000):
    pool.submit(req_test)

pool.shutdown(wait=True)

print("Done")
