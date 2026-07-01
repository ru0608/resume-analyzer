# 智能简历分析系统 - 阿里云函数计算 FC 自定义容器部署
# 使用 Python 3.10 slim 镜像

FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（PyMuPDF 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY . .

# FC 自定义容器监听端口
EXPOSE 9000

# 启动命令 - FC 健康检查需要监听 9000 端口
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
