# 使用Python官方镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装poetry
RUN pip install poetry@2.1.2

# 如果安装很慢，可以尝试使用清华镜像源
# RUN pip install poetry \
#   && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple


# 验证poetry是否安装成功
RUN poetry --version

# poetry config repositories.pypi https://pypi.tuna.tsinghua.edu.cn/simple


# 复制pyproject.toml和poetry.lock，并安装依赖
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# 复制项目文件到容器内
COPY . .

# 运行FastAPI应用
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
