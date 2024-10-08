from aiohttp import ClientTimeout

# 定义全局超时时间
TIMEOUT = ClientTimeout(total=600)