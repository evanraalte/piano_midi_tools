from collections.abc import Generator
from pathlib import Path
from types import TracebackType
from typing import Any

import cv2


class VideoCapture:
    def __init__(self, video_path: str | Path) -> None:
        self.video_path: Path = Path(video_path)
        self.cap: cv2.VideoCapture | None = None
        self._properties: dict[str, Any] = {}
        self._validate_file()

    def _validate_file(self) -> None:
        if not self.video_path.exists():
            msg = f"Video file not found: {self.video_path}"
            raise FileNotFoundError(msg)
        if not self.video_path.is_file():
            msg = f"Expected a file, got a directory: {self.video_path}"
            raise IsADirectoryError(msg)

    def _initialize_capture(self) -> None:
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            msg = f"Unable to open video file: {self.video_path}"
            raise OSError(msg)

        self._properties = {
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        }

    def __enter__(self) -> "VideoCapture":
        self._initialize_capture()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.release()

    def __str__(self) -> str:
        if not self._properties:
            return f"Uninitialized VideoCapture: {self.video_path.name}"
        return (
            f"Video: {self.video_path.name}\n"
            f"Dimensions: {self._properties['width']}x{self._properties['height']}\n"
            f"FPS: {self._properties['fps']}\n"
            f"Frame Count: {self._properties['frame_count']}"
        )

    def get_frame(self, frame_number: int) -> cv2.typing.MatLike:
        if not self.cap:
            msg = "VideoCapture is not initialized. Use with 'with' statement or call _initialize_capture() first."
            raise RuntimeError(msg)
        if frame_number < 0 or frame_number >= self._properties["frame_count"]:
            msg = f"Invalid frame number. Must be between 0 and {self._properties['frame_count'] - 1}"
            raise ValueError(msg)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if not ret:
            msg = f"Unable to read frame {frame_number}"
            raise OSError(msg)
        return frame

    def set_frame(self, frame_number: int) -> None:
        if not self.cap:
            msg = "VideoCapture is not initialized. Use with 'with' statement or call _initialize_capture() first."
            raise RuntimeError(msg)
        if frame_number < 0 or frame_number >= self._properties["frame_count"]:
            msg = f"Invalid frame number. Must be between 0 and {self._properties['frame_count'] - 1}"
            raise ValueError(msg)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def read_range(
        self, start: int, end: int
    ) -> Generator[cv2.typing.MatLike, None, None]:
        if not self.cap:
            msg = "VideoCapture is not initialized. Use with 'with' statement or call _initialize_capture() first."
            raise RuntimeError(msg)
        if start < 0 or end >= self._properties["frame_count"]:
            msg = f"Invalid frame range. Must be between 0 and {self._properties['frame_count'] - 1}"
            raise ValueError(msg)

        for frame_number in range(start, end):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            if not ret:
                msg = f"Unable to read frame {frame_number}"
                raise OSError(msg)
            yield frame

    def read(self) -> tuple[bool, cv2.typing.MatLike]:
        if not self.cap:
            msg = "VideoCapture is not initialized. Use with 'with' statement or call _initialize_capture() first."
            raise RuntimeError(msg)
        return self.cap.read()

    def release(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None

    @property
    def height(self) -> int | None:
        return self._properties.get("height")

    @property
    def width(self) -> int | None:
        return self._properties.get("width")

    @property
    def fps(self) -> float | None:
        return self._properties.get("fps")

    @property
    def frame_count(self) -> int | None:
        return self._properties.get("frame_count")
