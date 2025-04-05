import pytest

from piano_midi.models import KeyIndex


def test_white_key_maps_to_key_index() -> None:
    for n in range(52):
        KeyIndex.from_white_key_index(n)


def test_black_key_maps_to_key_index() -> None:
    for n in range(36):
        KeyIndex.from_black_key_index(n)


@pytest.mark.parametrize(
    ("black_key_index", "key_index"),
    [
        (0, 1),
        (1, 4),
        (2, 6),
        (3, 9),
        (4, 11),
    ],
)
def test_black_key_maps_correctly_to_key_index(
    black_key_index: int, key_index: int
) -> None:
    assert KeyIndex.from_black_key_index(black_key_index).value == key_index


@pytest.mark.parametrize(
    ("white_key_index", "key_index"),
    [
        (0, 0),
        (1, 2),
        (2, 3),
        (3, 5),
        (4, 7),
        (5, 8),
        (6, 10),
    ],
)
def test_white_key_maps_correctly_to_key_index(
    white_key_index: int, key_index: int
) -> None:
    assert KeyIndex.from_white_key_index(white_key_index).value == key_index
