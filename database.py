from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from models import Base
from config import settings


async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    pool_size=5,
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def create_tables():
    """Создает таблицы в базе данных асинхронно"""
    print("🔍 Проверяем существующие таблицы...")
    
    try:
        async with async_engine.begin() as conn:
            # Проверяем существование таблицы
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'posts'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ Таблица 'posts' уже существует, пропускаем создание")
            else:
                print("📝 Таблица 'posts' не найдена, создаем...")
                await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Таблицы проверены/созданы успешно")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise

async def get_db():
    """Dependency для получения асинхронной сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Тестовое подключение и создание таблиц
async def test_connection():
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("✅ Подключение к PostgreSQL успешно!")
            print(f"Версия: {version}")
        
        await create_tables()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection())