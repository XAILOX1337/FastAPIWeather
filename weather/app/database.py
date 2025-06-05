from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from sqlalchemy.ext.asyncio import AsyncEngine


DATABASE_URL = "postgresql+asyncpg://postgres:2007@localhost:1337/mydb"
database = Database(DATABASE_URL)



engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, autocommit=False, autoflush=False
)

Base = declarative_base()  # Базовый класс для моделей

async def create_tables():
    async_engine: AsyncEngine = engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Зависимость для получения асинхронной сессии
async def get_db():
    async_session = SessionLocal()
    try:
        yield async_session
    finally:
        await async_session.close()