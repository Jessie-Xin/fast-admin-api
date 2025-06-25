from dotenv import load_dotenv
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

    # 前端地址配置
    FRONTEND_URL: str = "http://localhost:3000"

    # 邮箱配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = "FastAdmin"

    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }


# 创建全局设置实例
settings = Settings()
