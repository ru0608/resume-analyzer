"""AI 赋能的智能简历分析系统 - 主应用入口

基于 FastAPI 的后端服务，支持部署到阿里云函数计算 FC。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import resume, match
from config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="支持简历 PDF 上传解析、AI 关键信息提取、岗位匹配度评分的智能分析系统",
)

# CORS 配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(resume.router)
app.include_router(match.router)


@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


# 阿里云函数计算入口
def handler(environ, start_response):
    """FC 函数计算入口适配"""
    from urllib.parse import parse_qs
    from io import BytesIO

    # 简单 FC 适配：生产环境建议使用 Web 框架适配层
    status = "200 OK"
    response_headers = [("Content-type", "application/json; charset=utf-8")]
    start_response(status, response_headers)
    return [b'{"service": "resume-analyzer", "status": "running"}']
