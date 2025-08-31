import faker
import pytest
from pydantic import ValidationError

from source.endpoints.encode import EncodeRequest

fake = faker.Faker()


@pytest.mark.parametrize(
    "payload, error_message",
    [
        ({"url": "link", "lifetime": None, "length": 1}, "Input should be a valid URL"),
        ({"url": fake.url(), "length": 1}, "Field required"),
        ({"url": fake.url(), "lifetime": -1, "length": 1}, "Input should be greater than 0"),
        ({"url": fake.url(), "lifetime": 1, "length": -1}, "Input should be greater than 0"),
    ],
)
def test_encode_request_raises_validation_error(payload: dict, error_message: str) -> None:
    with pytest.raises(ValidationError) as context:
        EncodeRequest(**payload)
    assert error_message in str(context.value)
