import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Blog API"
    APP_DESCRIPTION: str = "博客后台管理系统API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # 数据库配置
    DATABASE_URL: str
    
    # Markdown配置
    MARKDOWN_EXTENSIONS: str = "fenced_code,tables,nl2br"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings() 