from pathlib import Path

import mido

from piano_midi.piano_state import PianoChanges

A0_OFFSET = 21
VELOCITY = 64


class KeySequenceWriter:
    def __init__(self, fps: float) -> None:
        self.midi_file = mido.MidiFile()
        self.track = mido.MidiTrack()
        self.midi_file.tracks.append(self.track)
        self.current_frame = 0
        self.fps = fps
        self.start_key = 0
        self.end_key = 87  # Default to full 88-key range

    def set_key_range(self, start_key: int, end_key: int) -> None:
        """Set the key range to process. Keys outside this range will be ignored."""
        self.start_key = start_key
        self.end_key = end_key
        print(
            f"MIDI key range set: {self.to_note(start_key)} to {self.to_note(end_key)}"
        )

    def process_change(self, piano_changes: PianoChanges, frame_num: int) -> None:
        # Update time reference
        frame_diff = frame_num - self.current_frame
        self.current_frame = frame_num
        time_diff = int(1000 / self.fps * frame_diff)

        # Implementation for processing changes, filtering by key range
        for press in piano_changes.pressed:
            # Skip keys outside our range
            if press.index < self.start_key or press.index > self.end_key:
                continue

            self.track.append(
                mido.Message(
                    "note_on",
                    note=press.index + A0_OFFSET,
                    velocity=VELOCITY,
                    time=time_diff,
                )
            )
            time_diff = 0
            print(
                f"Key {press.index} ({self.to_note(press.index)}) pressed by {press.hand}"
            )
        for press in piano_changes.released:
            # Skip keys outside our range
            if press.index < self.start_key or press.index > self.end_key:
                continue

            self.track.append(
                mido.Message(
                    "note_off",
                    note=press.index + A0_OFFSET,
                    velocity=VELOCITY,
                    time=time_diff,
                )
            )
            time_diff = 0
            print(
                f"Key {press.index} ({self.to_note(press.index)}) released by {press.hand}"
            )
        print(f"during frame {frame_num}")

    def save(self, midi_file_path: Path) -> None:
        self.midi_file.save(midi_file_path)
        print(f"Saved midi file of {self.midi_file.length}s to {midi_file_path}")
        print(f"Expected length is {self.current_frame / self.fps}s")

    @staticmethod
    def to_note(key: int) -> str:
        notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

        # Octave 0 starts at key 0 (A0), so we directly calculate the octave
        octave = (key + 9) // 12  # Shifting by 9 because C is the start of an octave

        note = notes[key % 12]  # Calculate the note in that octave

        return f"{note}{octave}"
