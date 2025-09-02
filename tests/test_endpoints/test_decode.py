from collections.abc import Awaitable, Callable

from fastapi import status
from httpx import AsyncClient

from source.database.models import Link


async def test_decode__success(
    client: AsyncClient, random_url: str, random_code: int, link_factory: Callable[..., Awaitable[Link]]
) -> None:
    await link_factory(url=random_url, code=random_code)

    response = await client.get(f"/d/{random_code}")

    assert response.status_code == status.HTTP_308_PERMANENT_REDIRECT
    assert response.headers["location"] == random_url


async def test_decode__failure(client: AsyncClient, random_code: str) -> None:
    response = await client.get(f"/d/{random_code}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response_data = response.json()
    assert "detail" in response_data
    assert "There's no `link` assigned to this code" in response_data["detail"]
