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
        threshold: int = 5,
    ) -> bool:
        # Implementation for checking if a segment is 'on'
        return bool(
            np.count_nonzero(mask[:, key_segment.start : key_segment.end]) > threshold
        )

    def run(
        self,
        *,
        key_sequence_writer: KeySequenceWriter,
        scan_line_px: int = 100,
        frame_start: int,
        frame_end: int | None,
    ) -> None:
        with self.video_capture as cap:
            for frame, frame_num in cap.read_range(frame_start, frame_end):
                # read line  of frame
                line = frame[scan_line_px : scan_line_px + 1, :, :]
                line_hsv = cv2.cvtColor(line, cv2.COLOR_BGR2HSV)

                left_white = cv2.inRange(
                    line_hsv,
                    cast(HSVRange, self.key_colors.left_white).lower(),
                    cast(HSVRange, self.key_colors.left_white).upper(),
                )
                left_black = cv2.inRange(
                    line_hsv,
                    cast(HSVRange, self.key_colors.left_black).lower(),
                    cast(HSVRange, self.key_colors.left_black).upper(),
                )
                right_white = cv2.inRange(
                    line_hsv,
                    cast(HSVRange, self.key_colors.right_white).lower(),
                    cast(HSVRange, self.key_colors.right_white).upper(),
                )
                right_black = cv2.inRange(
                    line_hsv,
                    cast(HSVRange, self.key_colors.right_black).lower(),
                    cast(HSVRange, self.key_colors.right_black).upper(),
                )

                # # draw scan line in frame
                # cv2.line(frame, (0, scan_line_px), (frame.shape[1], scan_line_px), (0, 255, 0), 2)
                # cv2.imshow("frame", frame)
                # cv2.waitKey(0)

                next_piano_state = self.piano_state.copy()
                for key_idx, segment in enumerate(
                    cast(list[KeySegment], self.key_segments.white)
                ):
                    next_piano_state.set_white_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(left_white, segment),
                        hand=Hand.LEFT,
                    )
                    next_piano_state.set_white_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(right_white, segment),
                        hand=Hand.RIGHT,
                    )
                for key_idx, segment in enumerate(
                    cast(list[KeySegment], self.key_segments.black)
                ):
                    next_piano_state.set_black_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(left_black, segment),
                        hand=Hand.LEFT,
                    )
                    next_piano_state.set_black_key(
                        key_idx,
                        is_pressed=self._is_key_pressed(right_black, segment),
                        hand=Hand.RIGHT,
                    )

                changes = next_piano_state.detect_changes(self.piano_state)
                if changes.pressed or changes.released:
                    key_sequence_writer.process_change(changes, frame_num)
                self.piano_state = next_piano_state
