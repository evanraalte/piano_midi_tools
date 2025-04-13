from pathlib import Path

from piano_midi.color_picker import ColorPicker
from piano_midi.models import Hand, HSVRange, KeyColorIndex, PianoKeyColor, Range


def test_color_picker_can_store_color(tmp_path: Path) -> None:
    color_picker = ColorPicker(colors_path=tmp_path / "test.yml")
    key_color: KeyColorIndex = (PianoKeyColor.BLACK, Hand.LEFT)
    hsv_range = HSVRange(
        h=Range(min=0, max=0), s=Range(min=0, max=0), v=Range(min=0, max=0)
    )
    color_picker.save_color(
        key_color=key_color,
        hsv_range=hsv_range,
    )

    assert color_picker.load_color(key_color=key_color) == hsv_range
