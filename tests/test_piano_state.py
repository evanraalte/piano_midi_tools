import copy

import pytest

from piano_midi.models import Hand
from piano_midi.piano_state import PianoHandState, PianoKeyState, PianoState


def piano_factory() -> PianoState:
    return PianoState(key_state=PianoKeyState(), hand_state=PianoHandState())


@pytest.mark.parametrize(("num_keys_pressed"), [1, 2, 5])
def test_piano_white_keys_released(num_keys_pressed: int) -> None:
    piano_state = piano_factory()
    for n in range(num_keys_pressed):
        piano_state.set_white_key(n, is_pressed=True, hand=Hand.LEFT)

    piano_next_state = piano_factory()

    changes = piano_next_state.detect_changes(piano_state)
    assert len(changes.released) == num_keys_pressed
    assert len(changes.pressed) == 0


@pytest.mark.parametrize(("num_keys_pressed"), [1, 2, 5])
def test_piano_white_keys_pressed(num_keys_pressed: int) -> None:
    piano_state = piano_factory()

    piano_next_state = piano_factory()
    for n in range(num_keys_pressed):
        piano_next_state.set_white_key(n, is_pressed=True, hand=Hand.LEFT)

    changes = piano_next_state.detect_changes(piano_state)
    assert len(changes.released) == 0
    assert len(changes.pressed) == num_keys_pressed


def test_same_state_is_no_difference() -> None:
    piano_state = piano_factory()
    piano_state.set_white_key(0, is_pressed=True, hand=Hand.LEFT)

    changes = piano_state.detect_changes(piano_state)
    assert len(changes.released) == 0
    assert len(changes.pressed) == 0


def test_some_keys_pressed_and_released() -> None:
    piano_state = piano_factory()
    # 0 1 2 are pressed
    piano_state.set_white_key(0, is_pressed=True, hand=Hand.LEFT)
    piano_state.set_white_key(1, is_pressed=True, hand=Hand.LEFT)
    piano_state.set_white_key(2, is_pressed=True, hand=Hand.LEFT)

    # 1 2 are released, 3 is pressed
    piano_next_state = copy.deepcopy(piano_state)
    piano_next_state.set_white_key(1, is_pressed=False, hand=Hand.LEFT)
    piano_next_state.set_white_key(2, is_pressed=False, hand=Hand.LEFT)
    piano_next_state.set_white_key(3, is_pressed=True, hand=Hand.LEFT)

    changes = piano_next_state.detect_changes(piano_state)
    assert len(changes.released) == 2  # noqa: PLR2004
    assert len(changes.pressed) == 1
