import schedule
import time

from libs import sqlUtils
from loguru import logger

# 暂时未启用 还在设计更好的更新方式 zzz
def restart():
    print("执行 reStart 方法")
    sqlUtils.open_conn()
    sqlUtils.clear_data("paths")
    sqlUtils.clear_data("files")
    logger.info()
    sqlUtils.close_conn()


# 安排任务每天0点执行
schedule.every().day.at("00:00").do(restart)

while True:
    schedule.run_pending()
    time.sleep(1)
