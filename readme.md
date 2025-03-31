# ***随机图片API***
- 通过七牛云OSS实现获取随机图片

## 参数解释
 - ***参数具体格式见 .env.example 文件***
   - ***QINIU_ACCESS_KEY：*** 七牛云的AK
   - ***QINIU_SECRET_KEY：*** 七牛云的SK
   - ***QINIU_TEST_BUCKET：*** 七牛云存储桶名称
   - ***QINIU_CDN_URL：*** 七牛云CDN域名
   - ***QINIU_SOURCE_PATH：*** 图片文件存储路径
   - ***QINIU_SUFFIX：*** 图片预处理后缀-高质量
   - ***QINIU_TEMP_SUFFIX：*** 图片预处理后缀-低质量

## 启动方法
 ### 1. docker-compose 容器启动（推荐，简单）
 - 1.1. 下载项目代码
 - 1.2. 修改 .env 文件，配置参数
 - 1.3. 启动容器
   - `docker compose up --build -d`
 - 1.4. 访问 http://127.0.0.1:8000/docs 即可见到 API 文档
 - 1.5. 停止容器
   - `docker compose down`
   
 ### 2. 本地源码启动
 - 2.1. 下载项目代码
 - 2.2. 修改 .env 文件，配置参数
 - 2.3. 安装依赖包（要先安装 poetry，请自行安装 `https://python-poetry.org/docs/#installation`）
   - `poetry install`
 - 2.4. 启动项目
   - `poetry run uvicorn main:app --reload`
 - 2.5. 访问 http://127.0.0.1:8000/docs 即可见到 API 文档