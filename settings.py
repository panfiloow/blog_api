from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_HOST: str   
    DATABASE_PORT: str

    model_config = {
        "env_file": ".env", 
        "env_file_encoding": "utf-8",
    }

    @property
    def DATABASE_URL(self) -> str:
        """Формирует строку подключения к базе данных"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.POSTGRES_DB}"

settings = Settings()