from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.schemas.users import UserCreate, UserResponse, UserUpdate

from src.models.users import follows, User as UserORM  # noqa
from src.models.posts import Post  # noqa
from src.models.comments import Comment  # noqa

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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

    hashed_password = user_info.password

    new_user = UserORM(
        username=user_info.username,
        email=user_info.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserORM).options(
            selectinload(UserORM.posts),
            selectinload(UserORM.comments),
            selectinload(UserORM.following),
            selectinload(UserORM.followers)
        ).filter(UserORM.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).filter(UserORM.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username:
        user.username = user_update.username
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.hashed_password = user_update.password

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).filter(UserORM.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"detail": "User deleted"}

@router.post("/{user_id}/follow")
async def follow_user(user_id: int, current_user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).filter(UserORM.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(UserORM).options(selectinload(UserORM.following)).filter(UserORM.id == current_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    if target_user in current_user.following:
        raise HTTPException(status_code=400, detail="Already following")

    current_user.following.append(target_user)
    await db.commit()
    return {"detail": "Successfully followed"}


@router.delete("/{user_id}/unfollow")
async def unfollow_user(user_id: int, current_user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).filter(UserORM.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(UserORM).options(selectinload(UserORM.following)).filter(UserORM.id == current_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    if target_user not in current_user.following:
        raise HTTPException(status_code=400, detail="Not following")

    current_user.following.remove(target_user)
    await db.commit()
    return {"detail": "Successfully unfollowed"}


@router.get("/{user_id}/followers", response_model=List[UserResponse])
async def get_followers(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserORM).options(selectinload(UserORM.followers)).filter(UserORM.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.followers


@router.get("/{user_id}/following", response_model=List[UserResponse])
async def get_following(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserORM).options(selectinload(UserORM.following)).filter(UserORM.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.following