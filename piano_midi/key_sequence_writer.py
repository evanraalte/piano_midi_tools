from pathlib import Path

import typer


class KeySequenceWriter:
    def __init__(self, midi_file_path: Path) -> None:
        self.midi_file_path = midi_file_path
        self.pressed_keys: dict[int, int] = {}

    def press_white(self, key_idx: int, frame_num: int) -> None:
        if key_idx not in self.pressed_keys:
            typer.echo(f"frame {frame_num}: Pressing key {key_idx}")
            self.pressed_keys[key_idx] = frame_num

    def release_white(self, key_idx: int, frame_num: int) -> None:
        if key_idx in self.pressed_keys:
            typer.echo(
                f"frame {frame_num}: Releasing key {key_idx}, it was pressed for {frame_num - self.pressed_keys[key_idx]} frames"
            )
            self.pressed_keys.pop(key_idx)
