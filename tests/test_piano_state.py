from piano_midi.piano_state import PianoHandState, PianoKeyState, PianoState


def piano_factory() -> PianoState:
    return PianoState(key_state=PianoKeyState(), hand_state=PianoHandState())


def test_piano_black_key_is_released() -> None:
    # Black key 0 pressed
    piano_state = piano_factory()
    piano_state.set_black_key(0, is_pressed=True)

    piano_next_state = piano_factory()

    changes = piano_next_state.detect_changes(piano_state)
    assert changes.pressed == []
