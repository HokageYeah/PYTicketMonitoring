FROM python:3.10.10-slim

# 设置docker的工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt /app/

# 安装依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 设置环境变量
ENV ENV=production
ENV PYTHONUNBUFFERED=1

# 暴露端口（假设你的应用运行在5000端口）
EXPOSE 8001

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
