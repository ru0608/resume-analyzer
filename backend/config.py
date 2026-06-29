"""AI 赋能的智能简历分析系统 - 配置模块

环境变量配置，支持阿里云函数计算部署。
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "智能简历分析系统"
    app_version: str = "1.0.0"

    # DashScope (通义千问) 配置
    dashscope_api_key: str = ""
    dashscope_model: str = "qwen-plus"  # 或 qwen-turbo，qwen-max

    # Redis 缓存配置（可选）
    redis_host: Optional[str] = None
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    cache_ttl: int = 3600  # 缓存过期时间（秒）

    # 文件上传配置
    upload_dir: str = "/tmp/uploads"  # FC 环境下使用 /tmp
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # 评分权重配置
    weight_skill_match: float = 0.4
    weight_experience: float = 0.3
    weight_education: float = 0.15
    weight_keyword: float = 0.15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
