from piano_midi.midi_writer import KeySequenceWriter
from piano_midi.models import KeyColors, KeySegments
from piano_midi.video_capture import VideoCapture


class KeyPressDetector:
    def __init__(
        self,
        video_capture: VideoCapture,
        key_segments: KeySegments,
        key_colors: KeyColors,
    ) -> None:
        self.video_capture = video_capture
        self.key_segments = key_segments
        self.key_colors = key_colors

    def run(self, midi_writer: KeySequenceWriter) -> None:
        pass
