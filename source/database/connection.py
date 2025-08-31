from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from source.settings import settings


def build_url() -> str:
    return settings.database_url.replace("postgresql://", "postgresql+asyncpg://")


ENGINE = create_async_engine(
    build_url(),
    pool_pre_ping=True,  # validates connections before use
    pool_size=5,  # maximum number of persistent connections the pool keeps open
    max_overflow=10,  # extra connections the pool can open temporarily if all pool_size connections are busy
    pool_recycle=300,  # any connection older than 300 seconds (5 minutes) will be closed and replaced before reuse
)


AsyncSessionLocal = async_sessionmaker(bind=ENGINE, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
