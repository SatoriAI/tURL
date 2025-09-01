from fastapi import status
from httpx import AsyncClient


async def test_status(client: AsyncClient) -> None:
    response = await client.get("/status")
    assert response.status_code == status.HTTP_200_OK


async def test_throttle(client: AsyncClient) -> None:
    r1 = await client.get("/status")
    assert r1.status_code == status.HTTP_200_OK

    r2 = await client.get("/status")
    assert r2.status_code == status.HTTP_200_OK

    r3 = await client.get("/status")
    assert r3.status_code == status.HTTP_429_TOO_MANY_REQUESTS
