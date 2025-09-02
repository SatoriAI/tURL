from collections.abc import Awaitable, Callable

import pytest
from fastapi import status
from httpx import AsyncClient

from source.database.models import Link


async def test_info__success(
    client: AsyncClient, random_url: str, random_code: str, link_factory: Callable[..., Awaitable[Link]]
) -> None:
    await link_factory(url=random_url, code=random_code)

    response = await client.get(f"/info/{random_code}")

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["url"] == random_url
    assert "lifetime" in response_data
    assert "registered" in response_data
    assert "modified" in response_data
    assert "expires_at" in response_data
    assert "expires_in" in response_data
    assert "expired" in response_data


async def test_info__failure(client: AsyncClient, random_code: str) -> None:
    response = await client.get(f"/info/{random_code}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response_data = response.json()
    assert "detail" in response_data
    assert "There's no `link` assigned to this code or the link has been already revoked" in response_data["detail"]


@pytest.mark.parametrize("lifetime", [None, 30])
async def test_extend__success(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    client: AsyncClient,
    random_url: str,
    random_lifetime: int,
    random_code: str,
    link_factory: Callable[..., Awaitable[Link]],
    lifetime: int | None,
) -> None:
    await link_factory(url=random_url, code=random_code, lifetime=random_lifetime)

    response = await client.patch(f"/extend/{random_code}", json={"lifetime": lifetime})

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["url"] == random_url
    assert "lifetime" in response_data
    assert "registered" in response_data
    assert "modified" in response_data
    assert "expires_at" in response_data
    assert "expires_in" in response_data
    assert "expired" in response_data

    # Verify lifetime was updated correctly
    if lifetime is None:
        assert response_data["lifetime"] is None  # Should be set to infinite lifetime
    else:
        assert response_data["lifetime"] == random_lifetime + lifetime  # Should be original + extended


async def test_extend__failure(client: AsyncClient, random_lifetime: int, random_code: str) -> None:
    response = await client.patch(f"/extend/{random_code}", json={"lifetime": random_lifetime})

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response_data = response.json()
    assert "detail" in response_data
    assert "There's no `link` assigned to this code" in response_data["detail"]
