from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Схема для создания пользователя (ввод)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str # Это будет сырой пароль, который мы хэшируем перед сохранением

class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    # Указывает Pydantic использовать значения атрибутов ORM-объекта (например, SQLAlchemy)
    class Config:
        from_attributes = True # Pydantic v2: orm_mode -> from_attributes