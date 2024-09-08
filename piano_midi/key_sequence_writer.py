from pathlib import Path

from piano_midi.piano_state import PianoChanges


class KeySequenceWriter:
    def __init__(self, midi_file_path: Path) -> None:
        self.midi_file_path = midi_file_path

    def process_change(self, piano_changes: PianoChanges, frame_num: int) -> None:
        # Implementation for processing changes
        for press in piano_changes.pressed:
            print(f"Key {press.index} pressed by {press.hand}")
        for press in piano_changes.released:
            print(f"Key {press.index} released by {press.hand}")
        print(f"during frame {frame_num}")
