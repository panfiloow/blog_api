from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

# Явно импортируем модели, чтобы SQLAlchemy знал о них
from src.models.users import User as UserORM  # noqa
from src.models.posts import Post as PostORM  # noqa
from src.models.comments import Comment  # noqa

from src.schemas.posts import PostCreate, PostResponse, PostUpdate
from src.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_info: PostCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).filter(UserORM.id == post_info.author_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Author not found")

    new_post = PostORM(
        title=post_info.title,
        content=post_info.content,
        author_id=post_info.author_id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return new_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PostORM).options(
            selectinload(PostORM.author),
            selectinload(PostORM.comments)
        ).filter(PostORM.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    author_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(PostORM).offset(skip).limit(limit)

    filters = []
    if author_id:
        filters.append(PostORM.author_id == author_id)
    if start_date:
        filters.append(PostORM.created_at >= start_date)
    if end_date:
        filters.append(PostORM.created_at <= end_date)

    if filters:
        query = query.filter(and_(*filters))

    result = await db.execute(query)
    posts = result.scalars().all()
    return posts


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostORM).filter(PostORM.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_update.title:
        post.title = post_update.title
    if post_update.content:
        post.content = post_update.content

    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostORM).filter(PostORM.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()
    return {"detail": "Post deleted"}