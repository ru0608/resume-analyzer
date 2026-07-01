# 智能简历分析系统 - 阿里云函数计算 FC 自定义容器部署
# 使用 DaoCloud 镜像加速（阿里云 ACR 构建环境无法直接访问 docker.io）

FROM docker.m.daocloud.io/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（PyMuPDF 需要），使用阿里云 apt 镜像加速
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true \
    && apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装，使用阿里云 PyPI 镜像加速
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制后端代码
COPY . .

# FC 自定义容器监听端口
EXPOSE 9000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
