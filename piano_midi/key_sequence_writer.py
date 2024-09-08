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

    def process_change(self, piano_changes: PianoChanges, frame_num: int) -> None:
        # Update time reference
        frame_diff = frame_num - self.current_frame
        self.current_frame = frame_num
        time_diff = int(1000 / self.fps * frame_diff)

        # Implementation for processing changes
        for press in piano_changes.pressed:
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
