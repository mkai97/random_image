from dotenv import load_dotenv
from fastapi import FastAPI

from libs.logs import SimpleLoggerMiddleware
from libs.qnClient import QnClient
from libs.sqlUtils import SqlUtils

load_dotenv()

app = FastAPI()

# 添加中间件到FastAPI应用
app.add_middleware(SimpleLoggerMiddleware)


@app.get("/")
async def root():
    """
        启动服务并返回启动信息。
    """

    return {
        "message": "The service has started successfully!",
        "version": "1.0",
        'tips': "Please visit /docs to see the API documentation."}


@app.get("/getoneimage")
async def randomimage(quality="origin"):
    """
        根据请求从CDN获取图片并返回给客户端。

        参数:
        quality (string) origin 原图 temp 缩略图

        返回:
        image (StreamingResponse): 图片内容以流的形式返回。

        抛出:
        HTTPException: 如果无法从CDN获取图片，则抛出400错误。
    """

    # 初始化数据库
    sqlUtils = SqlUtils()
    sqlUtils.open_conn()
    sqlUtils.create_table()
    sqlUtils.close_conn()

    if quality == "origin":
        return QnClient().get_onefile_by_prefix()
    elif quality == "temp":
        return QnClient().get_onefile_by_temp_prefix()
    else:
        return {
            "message": "The quality is not supported!",
            "version": "1.0",
            'tips': "Please visit /docs to see the API documentation."}
