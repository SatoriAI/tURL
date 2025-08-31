from source.database.connection import build_url
from source.settings import settings


def test_build_url() -> None:
    assert build_url() == settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
