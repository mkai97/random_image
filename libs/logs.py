from urllib.request import Request

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from time import time

# 配置Loguru日志记录器
logger.add("logs/logfile.log", rotation="1 day")


def get_client_ip(request: Request) -> str:
    if 'x-forwarded-for' in request.headers:
        return request.headers['x-forwarded-for']
    return request.client.host if request.client.host else 'Unknown'


class SimpleLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time()
        response = await call_next(request)
        process_time = time() - start_time

        # 获取客户端IP地址，考虑到可能存在的代理
        client_host = get_client_ip(request)
        # 记录日志：客户端IP地址、HTTP请求方法、请求路径、响应状态码、处理时间
        logger.info(f"Client IP: {client_host}, "
                    f"Method: {request.method}, "
                    f"Path: {request.url.path}, "
                    f"Status: {response.status_code}, "
                    f"Time: {process_time:.2f}s")

        return response
