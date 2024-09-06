from pathlib import Path

import cv2
import numpy as np
import typer
import yaml

from piano_midi.models import ESC_KEY, HSVRange, Range


class ColorPicker:
    WIN_NAME_HSV_MASK_CREATOR = "HSV Mask Creator"
    WIN_NAME_ORIGINAL_IMAGE = "Original Image"

    def _set_trackbar_pos(self, hsv_range: HSVRange) -> None:
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
                h=Range(min=max(0, color[0] - 10), max=min(179, color[0] + 10)),
                s=Range(min=max(0, color[1] - 40), max=min(255, color[1] + 40)),
                v=Range(min=max(0, color[2] - 40), max=min(255, color[2] + 40)),
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

    def __init__(self, time_slice: np.ndarray, colors_path: Path) -> None:
        self.image = time_slice
        self.colors_path = colors_path
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

    def save_color(self, color_num: int, hsv_range: HSVRange) -> None:
        try:
            with self.colors_path.open("r") as file:
                colors = yaml.safe_load(file)
        except FileNotFoundError:
            colors = {}
        colors[color_num] = hsv_range.model_dump()
        with self.colors_path.open("w") as file:
            yaml.dump(colors, file)
        typer.echo(
            f"Color {color_num}, HSVRange: {hsv_range} stored in {self.colors_path}"
        )

    def load_color(self, color_num: int) -> None:
        try:
            with self.colors_path.open("r") as file:
                colors = yaml.safe_load(file)
        except FileNotFoundError:
            typer.echo(f"Colors file not found: {self.colors_path}")
            return
        try:
            hsv_range = HSVRange.model_validate(colors[color_num])
            self._set_trackbar_pos(hsv_range)
            typer.echo(f"Color {color_num} loaded from {self.colors_path}")
        except KeyError:
            typer.echo(f"Color {color_num} not found in {self.colors_path}")

    def reset(self) -> None:
        # reset trackbars
        self.create_trackbars()
        # remove entries from colors file
        with self.colors_path.open("w") as file:
            yaml.dump({}, file)
        typer.echo("Trackbars reset and colors file cleared")

    def loop(self) -> None:
        running = True
        while running:
            hsv_range = self._get_trackbar_pos()
            mask = cv2.inRange(self.hsv, hsv_range.lower(), hsv_range.upper())
            result = cv2.bitwise_and(self.image, self.image, mask=mask)

            cv2.imshow(self.WIN_NAME_HSV_MASK_CREATOR, result)
            cv2.imshow(self.WIN_NAME_ORIGINAL_IMAGE, self.image)

            key = cv2.waitKey(1) & 0xFF
            if key == ESC_KEY:
                running = False
            if key in (ord("1"), ord("2"), ord("3"), ord("4")):
                color_num = int(chr(key))
                self.save_color(color_num, hsv_range)
            if key in (ord("q"), ord("w"), ord("e"), ord("r")):
                values = {"q": 1, "w": 2, "e": 3, "r": 4}
                color_num = values[chr(key)]
                self.load_color(color_num)
            if key == ord("z"):
                self.reset()

        cv2.destroyAllWindows()

    def run(self) -> None:
        self.create_windows()
        self.create_trackbars()
        self.loop()