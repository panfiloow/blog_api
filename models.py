from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base # Импортируем Base из database.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # Сохраняем хешированный пароль
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"