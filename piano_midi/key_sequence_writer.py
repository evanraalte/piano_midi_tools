from pathlib import Path

from piano_midi.piano_state import PianoChanges


class KeySequenceWriter:
    def __init__(self, midi_file_path: Path) -> None:
        self.midi_file_path = midi_file_path

    def process_change(self, piano_changes: PianoChanges) -> None:
        # Implementation for processing changes
        pass
