from fastapi import status
from httpx import AsyncClient

from source.settings import settings


async def test_home(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == status.HTTP_308_PERMANENT_REDIRECT
    assert response.headers["location"] == settings.frontend
