from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from src.schemas.users import UserCreate, UserResponse
from src.models.users import User as UserORM
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from passlib.context import CryptContext 

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_info: UserCreate, db: AsyncSession = Depends(get_db)):
    result_username = await db.execute(
        select(UserORM).where(UserORM.username == user_info.username)
    )
    existing_user = result_username.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    result_email = await db.execute(
        select(UserORM).where(UserORM.email == user_info.email)
    )
    existing_email = result_email.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = UserORM(
        username=user_info.username,
        email=user_info.email,
        hashed_password=user_info.password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user