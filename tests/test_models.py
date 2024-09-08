import pytest

from piano_midi.models import BlackKeyIndex, WhiteKeyIndex


def test_white_key_maps_to_key_index() -> None:
    for n in range(52):
        WhiteKeyIndex(value=n).to_key_index()


def test_black_key_maps_to_key_index() -> None:
    for n in range(36):
        BlackKeyIndex(value=n).to_key_index()


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
def test_white_key_maps_correctly_to_key_index(
    black_key_index: int, key_index: int
) -> None:
    assert BlackKeyIndex(value=black_key_index).to_key_index().value == key_index
