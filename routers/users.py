from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Импортируем select для проверки уникальности
from database import get_db
from schemas import UserCreate, User # Импортируем схемы
from models import User as UserModel # Импортируем модель, переименовав для ясности
from crud import create_user # <-- Абсолютный импорт из корня (папки blog_api)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User) # Указываем схему для ответа
async def create_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверим, существует ли пользователь с таким email или username
    existing_user = await db.execute(
        select(UserModel).filter((UserModel.email == user.email) | (UserModel.username == user.username))
    )
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or Username already registered")

    # Создаем пользователя через CRUD-функцию
    db_user = await create_user(db, user)
    return db_user