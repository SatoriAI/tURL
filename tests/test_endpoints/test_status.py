from fastapi import status
from httpx import AsyncClient


async def test_status(client: AsyncClient) -> None:
    response = await client.get("/status")
    assert response.status_code == status.HTTP_200_OK
