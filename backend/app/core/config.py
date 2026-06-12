from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # config.py 路径: backend/app/core/config.py
    # 向上4层到项目根目录
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'db.sqlite')}"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
