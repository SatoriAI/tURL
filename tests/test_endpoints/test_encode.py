from collections.abc import Awaitable, Callable
from unittest.mock import patch

import faker
import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from source.database.models import Link
from source.endpoints.encode import EncodeRequest
from source.settings import settings

fake = faker.Faker()


@pytest.mark.parametrize(
    "payload, error_message",
    [
        # URL validation errors
        ({"url": "link", "lifetime": None, "length": 1}, "Input should be a valid URL"),
        ({"url": "", "lifetime": None, "length": 1}, "Input should be a valid URL"),
        ({"url": "not-a-url", "lifetime": None, "length": 1}, "Input should be a valid URL"),
        ({"url": "ftp://example.com", "lifetime": None, "length": 1}, "URL scheme should be 'http' or 'https'"),
        ({"url": "file:///path/to/file", "lifetime": None, "length": 1}, "URL scheme should be 'http' or 'https'"),
        ({"url": "http://", "lifetime": None, "length": 1}, "Input should be a valid URL"),
        ({"url": "https://", "lifetime": None, "length": 1}, "Input should be a valid URL"),
        # Missing required fields
        ({"url": fake.url(), "length": 1}, "Field required"),  # Missing lifetime
        ({"url": fake.url(), "lifetime": None}, "Field required"),  # Missing length
        ({}, "Field required"),  # All fields missing
        # Invalid lifetime values
        ({"url": fake.url(), "lifetime": -1, "length": 1}, "Input should be greater than 0"),
        ({"url": fake.url(), "lifetime": 0, "length": 1}, "Input should be greater than 0"),
        # Invalid length values
        ({"url": fake.url(), "lifetime": None, "length": -1}, "Input should be greater than 0"),
        ({"url": fake.url(), "lifetime": None, "length": 0}, "Input should be greater than 0"),
        # Non-integer values for PositiveInt fields
        ({"url": fake.url(), "lifetime": 1.5, "length": 1}, "Input should be a valid integer"),
        ({"url": fake.url(), "lifetime": None, "length": 1.5}, "Input should be a valid integer"),
        # Null/None values for required fields
        ({"url": None, "lifetime": None, "length": 1}, "URL input should be a string or URL"),
        ({"url": fake.url(), "lifetime": None, "length": None}, "Input should be a valid integer"),
        # Extra fields (should be ignored by Pydantic)
        ({"url": fake.url(), "lifetime": None, "length": 1, "extra_field": "ignored"}, None),
    ],
)
def test_encode_request_raises_validation_error(payload: dict, error_message: str | None) -> None:
    if error_message is None:
        EncodeRequest(**payload)
    else:
        with pytest.raises(ValidationError) as context:
            EncodeRequest(**payload)
        assert error_message in str(context.value)


async def test_encode__success(
    client: AsyncClient, random_url: str, random_lifetime: int, random_length: int, db_session: AsyncSession
) -> None:
    response = await client.post(
        "/encode", json={"url": random_url, "lifetime": random_lifetime, "length": random_length}
    )

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    assert "url" in response_data

    encoded_url = response_data["url"]
    assert encoded_url.startswith(settings.domain)
    assert len(encoded_url) > len(settings.domain)

    code = encoded_url.split("/")[-1]
    assert len(code) == random_length

    link = await db_session.scalar(select(Link).options(joinedload(Link.detail)).where(Link.code == code))
    assert link is not None
    assert link.url == random_url
    assert link.detail.length == random_length
    assert link.detail.lifetime == random_lifetime


async def test_encode__failure_max_attempts_exceeded(
    client: AsyncClient,
    random_url: str,
    random_length: int,
    random_code: int,
    link_factory: Callable[..., Awaitable[Link]],
) -> None:
    await link_factory(url=random_url, code=random_code)

    with patch("source.endpoints.encode.code") as mock_code:
        mock_code.return_value = random_code

        response = await client.post("/encode", json={"url": random_url, "lifetime": None, "length": random_length})

        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert mock_code.call_count == settings.max_code_generation_attempts

        response_data = response.json()
        assert "detail" in response_data
        assert "Could not generate a unique code" in response_data["detail"]
