from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from settings import settings
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    # echo=True # <-- Раскомментируйте, если хотите видеть SQL-запросы в логах
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as db: 
        yield db 