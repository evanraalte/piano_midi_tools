import numpy as np
import typer

from piano_midi.video_capture import VideoCapture


class TimeSlicer:
    def __init__(self, video_capture: VideoCapture) -> None:
        self.video_capture = video_capture

    def generate_timeslice(
        self, frame_start: int, frame_end: int | None, scan_line_pct: int
    ) -> np.ndarray:
        with self.video_capture as cap:
            if cap.height:
                scan_line_px = int(cap.height * scan_line_pct / 100)
            else:
                typer.echo(message="VideoCapture does not have a height")
                typer.Exit(code=1)
            _frame_start = frame_start or 0
            if cap.frame_count:
                _frame_end = min(frame_end or cap.frame_count - 1, cap.frame_count - 1)
            else:
                typer.echo(message="VideoCapture does not have a frame count")
                typer.Exit(code=1)

            timeslice = []

            cap.set_frame(_frame_start)
            for frame in cap.read_range(_frame_start, _frame_end):
                scan_line = frame[scan_line_px, :, :]
                timeslice.append(scan_line)

            return np.array(timeslice)
