import pytest

from source.utils.functions import code


@pytest.mark.parametrize(
    "length",
    [2, 4, 6, 8],
)
def test_code(length: int) -> None:
    generated_code = code(length=length)
    assert len(generated_code) == length
    assert isinstance(generated_code, str)
