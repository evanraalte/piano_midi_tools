import time  # Add this import
from pathlib import Path

import cv2
import numpy as np
import typer
import yaml

from piano_midi.models import (
    ESC_KEY,
    Hand,
    HSVRange,
    KeyColorIndex,
    KeyColors,
    PianoKeyColor,
    Range,
)


class ColorPicker:
    WIN_NAME_HSV_MASK_CREATOR = "HSV Mask Creator"
    WIN_NAME_ORIGINAL_IMAGE = "Original Image"

    def _set_trackbar_pos(self, hsv_range: HSVRange | None) -> None:
        if hsv_range is None:
            return
        cv2.setTrackbarPos("HMin", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.h.min)
        cv2.setTrackbarPos("SMin", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.s.min)
        cv2.setTrackbarPos("VMin", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.v.min)
        cv2.setTrackbarPos("HMax", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.h.max)
        cv2.setTrackbarPos("SMax", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.s.max)
        cv2.setTrackbarPos("VMax", self.WIN_NAME_HSV_MASK_CREATOR, hsv_range.v.max)

    def _get_trackbar_pos(self) -> HSVRange:
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
            color = self.hsv[y, x]
            print(f"Clicked color HSV: {color}")

            hsv_range = HSVRange(
                h=Range(
                    min=max(0, int(color[0]) - 10), max=min(179, int(color[0]) + 10)
                ),
                s=Range(
                    min=max(0, int(color[1]) - 40), max=min(255, int(color[1]) + 40)
                ),
                v=Range(
                    min=max(0, int(color[2]) - 40), max=min(255, int(color[2]) + 40)
                ),
            )
            self._set_trackbar_pos(hsv_range)

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

    def create_windows(self) -> None:
        cv2.namedWindow(self.WIN_NAME_ORIGINAL_IMAGE)
        cv2.namedWindow(self.WIN_NAME_HSV_MASK_CREATOR)
        cv2.setMouseCallback(self.WIN_NAME_ORIGINAL_IMAGE, self.click_event)

    def __init__(self, colors_path: Path) -> None:
        self.colors_path = colors_path
        self.last_process_time: float = 0  # Track the last processing time
        self.throttle_delay: float = 0.05  # Throttle delay in seconds (50ms)

    def set_timeslice(self, timeslice: np.ndarray) -> None:
        self.timeslice = timeslice
        self.hsv = cv2.cvtColor(self.timeslice, cv2.COLOR_BGR2HSV)

    def save_color(self, key_color: KeyColorIndex, hsv_range: HSVRange) -> None:
        key_colors = KeyColors.from_yaml(self.colors_path)
        key_colors.set_color(key_color, hsv_range)
        key_colors.to_yaml(self.colors_path)
        typer.echo(f"{key_color} with {hsv_range} stored in {self.colors_path}")

    def load_color(self, key_color: KeyColorIndex) -> None:
        key_colors = KeyColors.from_yaml(self.colors_path)
        hsv_range = key_colors.get_color(key_color)
        self._set_trackbar_pos(hsv_range)
        return hsv_range

    def reset(self) -> None:
        # reset trackbars
        self.create_trackbars()
        # remove entries from colors file
        with self.colors_path.open("w") as file:
            yaml.dump({}, file)
        typer.echo("Trackbars reset and colors file cleared")

    def loop(self) -> None:
        running = True
        last_hsv_range = None
        result = None

        while running:
            hsv_range = self._get_trackbar_pos()
            current_time = time.time()
            time_since_last_process = current_time - self.last_process_time

            # Only recalculate mask and result if HSV range has changed AND enough time has passed
            if (
                last_hsv_range is None or hsv_range != last_hsv_range
            ) and time_since_last_process >= self.throttle_delay:
                mask = cv2.inRange(self.hsv, hsv_range.lower(), hsv_range.upper())
                result = cv2.bitwise_and(self.timeslice, self.timeslice, mask=mask)
                last_hsv_range = hsv_range
                self.last_process_time = current_time

            cv2.imshow(self.WIN_NAME_HSV_MASK_CREATOR, result)
            cv2.imshow(self.WIN_NAME_ORIGINAL_IMAGE, self.timeslice)

            key = (
                cv2.waitKey(30) & 0xFF
            )  # Increased from 10ms to 30ms for better processing time
            if key == ESC_KEY:
                running = False
            key_char = chr(key)
            mapping = [
                (PianoKeyColor.WHITE, Hand.LEFT),
                (PianoKeyColor.BLACK, Hand.LEFT),
                (PianoKeyColor.WHITE, Hand.RIGHT),
                (PianoKeyColor.BLACK, Hand.RIGHT),
            ]
            if key_char in "1234":  # save
                idx = key - ord("1")
                self.save_color(key_color=mapping[idx], hsv_range=hsv_range)
            elif key_char == "q":
                self.load_color(key_color=mapping[0])
            elif key_char == "w":
                self.load_color(key_color=mapping[1])
            elif key_char == "e":
                self.load_color(key_color=mapping[2])
            elif key_char == "r":
                self.load_color(key_color=mapping[3])
            elif key_char == "z":
                self.reset()
                last_hsv_range = None  # Force recalculation after reset

        cv2.destroyAllWindows()

    def run(self) -> None:
        self.create_windows()
        self.create_trackbars()
        self.loop()
