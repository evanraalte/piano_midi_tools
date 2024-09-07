from piano_midi.models import BlackKeyIndex, WhiteKeyIndex


def test_white_key_maps_to_correct_key_index() -> None:
    for n in range(1, 52):
        WhiteKeyIndex(value=n).to_key_index()


def test_black_key_maps_to_correct_key_index() -> None:
    for n in range(1, 36):
        BlackKeyIndex(value=n).to_key_index()
