"""
配置管理模块
通过环境变量加载应用配置
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    APP_NAME: str = "DataQuark Stock Analysis API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "为AI Agent提供完整的A股股票分析数据"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # 缓存配置
    CACHE_TTL: int = 300  # 缓存时间（秒）
    MAX_CACHE_SIZE: int = 1000  # 最大缓存条目数
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    
    # 请求配置
    REQUEST_TIMEOUT: int = 30  # 请求超时时间（秒）
    MAX_CONCURRENT_REQUESTS: int = 10  # 最大并发请求数
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings() 