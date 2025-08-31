from random import sample
from string import ascii_letters, digits


def code(length: int) -> str:
    return "".join(sample(ascii_letters + digits, length))
