import numpy as np

from piano_midi.key_sequence_writer import KeySequenceWriter
from piano_midi.models import KeyColors, KeySegment, KeySegments
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
        self.scan_line_px = 100

    def _is_segment_on(self, left_white: np.ndarray, key_segment: KeySegment) -> bool:
        # Implementation for checking if a segment is 'on'
        return bool(np.any(left_white[:, key_segment.start : key_segment.end]) > 0)

    def run(
        self, *, key_sequence_writer: KeySequenceWriter, debug: bool = False
    ) -> None:
        pass
        # with self.video_capture as cap:
        #     for frame, frame_num in cap.read_range(0, 400):
        #         # read line  of frame
        #         line = frame[self.scan_line_px : self.scan_line_px + 1, :, :]
        #         line_hsv = cv2.cvtColor(line, cv2.COLOR_BGR2HSV)

        # if debug:
        #     frame_cut = frame[100:200, :, :]
        #     frame_cut_hsv = cv2.cvtColor(frame_cut, cv2.COLOR_BGR2HSV)
        #     frame_cut_hsv_filtered = cv2.inRange(frame_cut_hsv, self.key_colors.right_white.lower(), self.key_colors.right_white.upper())
        #     cv2.imshow("frame_cut", frame_cut_hsv_filtered)
        #     cv2.waitKey(0)

        # left_white = cv2.inRange(line_hsv, self.key_colors.left_white.lower(), self.key_colors.left_white.upper())
        # left_black = cv2.inRange(line_hsv, self.key_colors.left_black.lower(), self.key_colors.left_black.upper())
        # right_white = cv2.inRange(line_hsv, self.key_colors.right_white.lower(), self.key_colors.right_white.upper())
        # right_black = cv2.inRange(line_hsv, self.key_colors.right_black.lower(), self.key_colors.right_black.upper())

        # for key_idx, segment in enumerate(self.key_segments.white):
        #     # check if the segment is pressed (ie the segment range is 'on' in the entire'left_white')
        #     for _hand, channel in [(Hand.LEFT, left_white), (Hand.RIGHT, right_white)]:
        #         segment_on = self._is_segment_on(channel, segment)
        #         if segment_on:
        #             key_sequence_writer.press_white(key_idx, frame_num=frame_num)
        #         else:
        #             key_sequence_writer.release_white(key_idx, frame_num=frame_num)
