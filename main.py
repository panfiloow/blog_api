from typing import List, AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Post as PostModel
from database import get_db, create_tables
from config import settings

# Lifespan менеджер
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: создаем таблицы при запуске
    print("🚀 Starting up... Creating tables")
    await create_tables()
    yield
    # Shutdown: можно добавить логику закрытия
    print("🔴 Shutting down...")

app = FastAPI(
    title="Blog API", 
    version="1.0.0",
    lifespan=lifespan
)

class CreatePost(BaseModel):
    title: str
    content: str
    published: bool = True

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    last_update: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)

@app.get("/")
async def root():
    return {"status": "server work"}

@app.get("/posts", response_model=List[PostResponse])
async def get_posts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostModel).offset(skip).limit(limit))
    posts = result.scalars().all()
    return posts

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пост не найден"
        )
    return post

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: CreatePost, db: AsyncSession = Depends(get_db)):
    db_post = PostModel(
        title=post.title,
        content=post.content,
        published=post.published,
        created_at=datetime.now()
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return {"msg": "Пост успешно создан", "id": db_post.id}

@app.put("/posts/{post_id}")
async def change_post(post_id: int, update: CreatePost, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пост не найден"
        )
    
    db_post.title = update.title
    db_post.content = update.content
    db_post.published = update.published
    db_post.last_update = datetime.now()
    
    await db.commit()
    await db.refresh(db_post)
    
    return {"msg": "Пост изменен", "post": PostResponse.model_validate(db_post)}

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пост не найден"
        )
    
    await db.delete(db_post)
    await db.commit()
    
    return {"msg": "Пост успешно удален"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True
    )