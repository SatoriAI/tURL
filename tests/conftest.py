from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import faker
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from source.app import create_app
from source.database.connection import get_session as get_session_dependency
from source.database.models import Base, Detail, Link
from source.settings import settings

fake = faker.Faker()


@pytest.fixture(name="engine")
async def fixture_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"), poolclass=NullPool
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(name="app", scope="function")
def fixture_app(engine: AsyncEngine) -> FastAPI:
    application = create_app()

    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session

    application.dependency_overrides[get_session_dependency] = override_get_session
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        await transport.aclose()


@pytest.fixture(autouse=True)
async def setup_database(engine: AsyncEngine) -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):  # Delete all data from tables instead of recreating schema
            await conn.execute(delete(table))


@pytest.fixture(name="db_session")
async def fixture_db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
def random_url() -> str:
    return fake.url()


@pytest.fixture
def random_lifetime() -> int:
    return fake.pyint(min_value=1, max_value=100)


@pytest.fixture
def random_length() -> int:
    return fake.pyint(min_value=2, max_value=8)


@pytest.fixture
def random_code() -> str:
    return fake.pystr(min_chars=5, max_chars=10)


@pytest.fixture
def link_factory(db_session: AsyncSession) -> Callable[..., Awaitable[Link]]:
    async def factory(
        *,
        url: str = fake.url(),
        code: str = fake.pystr(min_chars=2, max_chars=8),
        length: int = fake.pyint(min_value=2, max_value=8),
        lifetime: int = fake.pyint(min_value=2, max_value=10),
    ) -> Link:
        link = Link(url=url, code=code, detail=Detail(length=length, lifetime=lifetime))
        db_session.add(link)
        await db_session.commit()
        return link

    return factory
