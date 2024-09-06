from pathlib import Path

import cv2
import numpy as np
import typer
from numpy import ndarray

from piano_midi.models import (
    ESC_KEY,
    HSVRange,
    InvalidNumOfKeySegmentsError,
    KeySegment,
    KeySegments,
    PianoKey,
    Range,
)


class KeyPicker:
    WIN_NAME_HSV_MASK_CREATOR = "HSV Mask Creator"

    def _get_scanline_pct(self) -> int:
        return cv2.getTrackbarPos("h_scanline_pct", self.WIN_NAME_HSV_MASK_CREATOR)

    def _set_scanline_pct(self, pct: int) -> None:
        cv2.setTrackbarPos("h_scanline_pct", self.WIN_NAME_HSV_MASK_CREATOR, pct)

    def _set_hsv_trackbar_pos(self, hsv_range: HSVRange) -> None:
        cv2.setTrackbarPos("HMin", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.h.min)
        cv2.setTrackbarPos("SMin", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.s.min)
        cv2.setTrackbarPos("VMin", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.v.min)
        cv2.setTrackbarPos("HMax", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.h.max)
        cv2.setTrackbarPos("SMax", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.s.max)
        cv2.setTrackbarPos("VMax", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.v.max)

    def _get_hsv_trackbar_pos(self) -> HSVRange:
        h_min = cv2.getTrackbarPos("HMin", self.WIN_NAME_HSV_MASK_CREATOR)
        s_min = cv2.getTrackbarPos("SMin", self.WIN_NAME_HSV_MASK_CREATOR)
        v_min = cv2.getTrackbarPos("VMin", self.WIN_NAME_HSV_MASK_CREATOR)
        h_max = cv2.getTrackbarPos("HMax", self.WIN_NAME_HSV_MASK_CREATOR)
        s_max = cv2.getTrackbarPos("SMax", self.WIN_NAME_HSV_MASK_CREATOR)
        v_max = cv2.getTrackbarPos("VMax", self.WIN_NAME_HSV_MASK_CREATOR)
        return HSVRange(
            h=Range(min=h_min, max=h_max),
            s=Range(min=s_min, max=s_max),
            v=Range(min=v_min, max=v_max),
        )

    def click_event(self, event, x, y, flags, param) -> None:  # noqa: ANN001, ARG002
        if event == cv2.EVENT_LBUTTONDOWN:
            # sets the scanline to the clicked y position
            self._set_scanline_pct(pct=y * 100 // self.image_height)

    def create_trackbars(self) -> None:
        cv2.createTrackbar(
            "HMin", self.WIN_NAME_HSV_MASK_CREATOR, 0, 179, lambda _: None
        )
        cv2.createTrackbar(
            "HMax", self.WIN_NAME_HSV_MASK_CREATOR, 179, 179, lambda _: None
        )
        cv2.createTrackbar(
            "SMin", self.WIN_NAME_HSV_MASK_CREATOR, 0, 255, lambda _: None
        )
        cv2.createTrackbar(
            "SMax", self.WIN_NAME_HSV_MASK_CREATOR, 255, 255, lambda _: None
        )
        cv2.createTrackbar(
            "VMin", self.WIN_NAME_HSV_MASK_CREATOR, 0, 255, lambda _: None
        )
        cv2.createTrackbar(
            "VMax", self.WIN_NAME_HSV_MASK_CREATOR, 255, 255, lambda _: None
        )

        cv2.createTrackbar(
            "h_scanline_pct", self.WIN_NAME_HSV_MASK_CREATOR, 0, 100, lambda _: None
        )

    def _create_windows(self) -> None:
        cv2.namedWindow(self.WIN_NAME_HSV_MASK_CREATOR)
        cv2.setMouseCallback(self.WIN_NAME_HSV_MASK_CREATOR, self.click_event)

    def __init__(self, frame: np.ndarray, key_segments_path: Path) -> None:
        self.image = frame
        self.key_segments_path = key_segments_path
        self.image_height = self.image.shape[0]
        self.image_width = self.image.shape[1]
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

    def _reset(self) -> None:
        # reset trackbars
        self.create_trackbars()
        typer.echo("Trackbars reset")

    def _store_segments(
        self, key_segments: list[KeySegment], piano_key: PianoKey
    ) -> None:
        """Stores the segments in a yaml file"""
        try:
            _key_segments = KeySegments.from_yaml(self.key_segments_path)
        except Exception:
            typer.echo("Could not load key segments, creating new one")
            _key_segments = KeySegments()
        try:
            setattr(_key_segments, piano_key.name.lower(), key_segments)
            _key_segments.to_yaml(self.key_segments_path)
            typer.echo(f"Segments stored for color {piano_key}")
        except InvalidNumOfKeySegmentsError as e:
            typer.echo(e, err=True)

    def _get_key_segments(self, masked_scanline: ndarray) -> list[KeySegment]:
        # first map every non zero value to white
        masked_scanline = (masked_scanline != 0) * 255
        white = np.array([255, 255, 255])
        segments = []
        start = None
        for i, row in enumerate(masked_scanline):
            if np.array_equal(row, white):
                if start is None:
                    start = i
            elif start is not None:
                segments.append((start, i - 1))
                start = None

        if start is not None:
            segments.append((start, len(masked_scanline) - 1))
        # filter out segments that are too small, for black keys this is 1/128 of the image width, so this holds for white keys as well
        noise_floor = self.image_width // 128
        segments = [
            segment for segment in segments if segment[1] - segment[0] > noise_floor
        ]
        key_segments = [
            KeySegment(start=segment[0], end=segment[1]) for segment in segments
        ]
        return key_segments

    def _loop(self) -> None:
        running = True
        while running:
            hsv_range = self._get_hsv_trackbar_pos()
            height_pct = self._get_scanline_pct()
            height_px = int(self.image_height * height_pct / 100) - 1
            mask = cv2.inRange(self.hsv, hsv_range.lower(), hsv_range.upper())
            masked_image = cv2.bitwise_and(self.image, self.image, mask=mask)
            # on the result, every non black pixel is white
            # so we can use the scanline to find the segments
            # draw line
            # make a copy of the image
            masked_image_with_overlay = masked_image.copy()
            cv2.line(
                masked_image_with_overlay,
                (0, height_px),
                (self.image.shape[1], height_px),
                (0, 255, 0),
                2,
            )

            # save a copy of result, with intersection of scanline (ie 1d array)
            line = masked_image[height_px, :, :]
            key_segments = self._get_key_segments(masked_scanline=line)

            # draw number of segments somewhere on the image
            cv2.putText(
                masked_image_with_overlay,
                f"Num of segments: {len(key_segments)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            # draw segments on result_with_line in red:
            # specifically, draw thick dots on the start and end of each segment
            for segment in key_segments:
                cv2.circle(
                    masked_image_with_overlay,
                    (segment.start, height_px),
                    5,
                    (0, 0, 255),
                    -1,
                )
                cv2.circle(
                    masked_image_with_overlay,
                    (segment.end, height_px),
                    5,
                    (255, 0, 0),
                    -1,
                )
            cv2.imshow(self.WIN_NAME_HSV_MASK_CREATOR, masked_image_with_overlay)

            # show segments on image

            key = cv2.waitKey(1) & 0xFF
            if key == ESC_KEY:
                running = False
            if key == ord("w"):
                self._store_segments(key_segments, PianoKey.WHITE)
            if key == ord("b"):
                self._store_segments(key_segments, PianoKey.BLACK)
            if key == ord("z"):
                self._reset()

        cv2.destroyAllWindows()

    def run(self) -> None:
        self._create_windows()
        self.create_trackbars()
        self._loop()
