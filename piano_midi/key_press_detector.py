from typing import cast

import cv2
import numpy as np

from piano_midi.key_sequence_writer import KeySequenceWriter
from piano_midi.models import Hand, HSVRange, KeyColors, KeySegment, KeySegments
from piano_midi.piano_state import PianoState
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

        self.piano_state = PianoState()

    def _is_key_pressed(
        self,
        mask: np.ndarray,
        key_segment: KeySegment,
    ) -> bool:
        threshold = self.video_capture.width // 256  # avoid glitches
        return (
            np.count_nonzero(mask[:, key_segment.start_px : key_segment.end_px])
            > threshold
        )

    def run(
        self,
        *,
        key_sequence_writer: KeySequenceWriter,
        scan_line_px: int = 100,
        frame_start: int,
        frame_end: int | None,
        start_key: int = 0,
        end_key: int = 87,
    ) -> None:
        with self.video_capture as cap:
            # Set key range in the key sequence writer
            key_sequence_writer.set_key_range(start_key, end_key)

            for frame, frame_num in cap.read_range(frame_start, frame_end):
                # read line  of frame
                line = frame[scan_line_px : scan_line_px + 1, :, :]
                line_hsv = cv2.cvtColor(line, cv2.COLOR_BGR2HSV)

                white_left = cv2.inRange(
                    line_hsv,
                    cast("HSVRange", self.key_colors.white_left).lower(),
                    cast("HSVRange", self.key_colors.white_left).upper(),
                )
                black_left = cv2.inRange(
                    line_hsv,
                    cast("HSVRange", self.key_colors.black_left).lower(),
                    cast("HSVRange", self.key_colors.black_left).upper(),
                )
                white_right = cv2.inRange(
                    line_hsv,
                    cast("HSVRange", self.key_colors.white_right).lower(),
                    cast("HSVRange", self.key_colors.white_right).upper(),
                )
                black_right = cv2.inRange(
                    line_hsv,
                    cast("HSVRange", self.key_colors.black_right).lower(),
                    cast("HSVRange", self.key_colors.black_right).upper(),
                )

                # # draw scan line in frame
                # cv2.line(frame, (0, scan_line_px), (frame.shape[1], scan_line_px), (0, 255, 0), 2)
                # cv2.imshow("frame", frame)
                # cv2.waitKey(0)

                next_piano_state = self.piano_state.copy()
                for key_idx, segment in enumerate(
                    cast("list[KeySegment]", self.key_segments.white)
                ):
                    next_piano_state.set_white_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(white_left, segment),
                        hand=Hand.LEFT,
                    )
                    next_piano_state.set_white_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(white_right, segment),
                        hand=Hand.RIGHT,
                    )
                for key_idx, segment in enumerate(
                    cast("list[KeySegment]", self.key_segments.black)
                ):
                    next_piano_state.set_black_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(black_left, segment),
                        hand=Hand.LEFT,
                    )
                    next_piano_state.set_black_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(black_right, segment),
                        hand=Hand.RIGHT,
                    )

                changes = next_piano_state.detect_changes(self.piano_state)
                if changes.pressed or changes.released:
                    key_sequence_writer.process_change(changes, frame_num)
                self.piano_state = next_piano_state
