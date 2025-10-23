
# slow_logger.py
import time
import logging
from typing import Optional, List
from fastapi import FastAPI, Request
from fastapi.responses import Response

def add_slow_request_logger(
    app: FastAPI,
    logger: logging.Logger,
    *,
    threshold: float = 1.0,
    path_prefixes: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
) -> None:
    """
    为 FastAPI 应用添加慢请求日志中间件（可选路径过滤）

    :param app: FastAPI 应用实例
    :param threshold: 慢请求阈值（秒），默认 1.0
    :param path_prefixes: 仅监控这些前缀的路径（如 ["/api"]），None 表示监控所有
    :param logger: 自定义日志器，None 则使用默认
    :param exclude_paths: 排除的路径列表（如 ["/health"]）
    """


    exclude_paths = exclude_paths or []
    path_prefixes = path_prefixes or []

    @app.middleware("http")
    async def slow_request_middleware(request: Request, call_next):
        # 跳过排除的路径
        for exclude in exclude_paths:
            if request.url.path.startswith(exclude):
                return await call_next(request)

        # 如果指定了 path_prefixes，只监控匹配的路径
        if path_prefixes:
            matched = any(request.url.path.startswith(prefix) for prefix in path_prefixes)
            if not matched:
                return await call_next(request)

        start_time = time.time()
        try:
            response: Response = await call_next(request)
        except Exception:
            # 即使出错也记录耗时
            process_time = time.time() - start_time
            if process_time > threshold:
                logger.log(
                    logging.ERROR,
                    f"Slow request (error): {request.method} {request.url.path} | "
                    f"Duration: {process_time:.3f}s | "
                    f"Client: {request.client.host if request.client else 'unknown'}"
                )
            raise

        process_time = time.time() - start_time

        if process_time > threshold:
            logger.log(
                logging.WARNING,
                f"Slow request: {request.method} {request.url.path} | "
                f"Duration: {process_time:.3f}s | "
                f"Status: {response.status_code} | "
                f"Client: {request.client.host if request.client else 'unknown'}"
            )

        return response