from pathlib import Path


class KeySequenceWriter:
    def __init__(self, midi_file_path: Path) -> None:
        self.midi_file_path = midi_file_path
