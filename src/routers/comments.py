from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional

# Явно импортируем модели, чтобы SQLAlchemy знал о них
from src.models.users import User as UserORM  # noqa
from src.models.posts import Post as PostORM  # noqa
from src.models.comments import Comment as CommentORM  # noqa

from src.schemas.comments import CommentCreate, CommentResponse, CommentUpdate
from src.database import get_db

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(comment_info: CommentCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).filter(UserORM.id == comment_info.author_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Author not found")

    result = await db.execute(select(PostORM).filter(PostORM.id == comment_info.post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = CommentORM(
        content=comment_info.content,
        author_id=comment_info.author_id,
        post_id=comment_info.post_id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    return new_comment


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CommentORM).options(
            selectinload(CommentORM.author),
            selectinload(CommentORM.post)
        ).filter(CommentORM.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    skip: int = 0,
    limit: int = 10,
    post_id: Optional[int] = None,
    author_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(CommentORM).offset(skip).limit(limit)

    filters = []
    if post_id:
        filters.append(CommentORM.post_id == post_id)
    if author_id:
        filters.append(CommentORM.author_id == author_id)

    if filters:
        query = query.filter(and_(*filters))

    result = await db.execute(query)
    comments = result.scalars().all()
    return comments


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_update: CommentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommentORM).filter(CommentORM.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment_update.content:
        comment.content = comment_update.content

    await db.commit()
    await db.refresh(comment)
    return comment


@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommentORM).filter(CommentORM.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    await db.delete(comment)
    await db.commit()
    return {"detail": "Comment deleted"}