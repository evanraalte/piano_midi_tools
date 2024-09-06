from pathlib import Path
from typing import Annotated

import cv2
import numpy as np
import typer
import yaml
from pydantic import BaseModel


class Range(BaseModel):
    min: int
    max: int


class HSVRange(BaseModel):
    h: Range
    s: Range
    v: Range

    def lower(self) -> np.ndarray:
        return np.array([self.h.min, self.s.min, self.v.min])
    def upper(self) -> np.ndarray:
        return np.array([self.h.max, self.s.max, self.v.max])

ESC_KEY = 27


# Convert to HSV
# HSV Format:
# H: Hue - color type (such as red, blue, or yellow).
#    In OpenCV it ranges from 0 to 179.
# S: Saturation - vibrancy of the color (0-255).
#    0 is white/gray, 255 is the full color.
# V: Value - brightness of the color (0-255).
#    0 is black, 255 is the brightest.

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
        cv2.createTrackbar("HMin", self.WIN_NAME_HSV_MASK_CREATOR, 0, 179, lambda _: None)
        cv2.createTrackbar("HMax", self.WIN_NAME_HSV_MASK_CREATOR, 179, 179, lambda _: None)
        cv2.createTrackbar("SMin", self.WIN_NAME_HSV_MASK_CREATOR, 0, 255, lambda _: None)
        cv2.createTrackbar("SMax", self.WIN_NAME_HSV_MASK_CREATOR, 255, 255, lambda _: None)
        cv2.createTrackbar("VMin", self.WIN_NAME_HSV_MASK_CREATOR, 0, 255, lambda _: None)
        cv2.createTrackbar("VMax", self.WIN_NAME_HSV_MASK_CREATOR, 255, 255, lambda _: None)

    def create_windows(self) -> None:
        cv2.namedWindow(self.WIN_NAME_ORIGINAL_IMAGE)
        cv2.namedWindow(self.WIN_NAME_HSV_MASK_CREATOR)
        cv2.setMouseCallback(self.WIN_NAME_ORIGINAL_IMAGE, self.click_event)

    def __init__(self, image_path: Path, colors_path: Path) -> None:
        self.image_path = image_path
        self.colors_path = colors_path
        self.image = cv2.imread(str(image_path))
        if self.image is None:
            msg = f"Could not read the image: {image_path}"
            raise ValueError(msg)
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
        print(f"Color {color_num} stored in {self.colors_path}")

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
        cv2.destroyAllWindows()

    def run(self) -> None:
        self.create_windows()
        self.create_trackbars()
        self.loop()

app = typer.Typer()
@app.command()
def start(
    *,
    image_path: Annotated[
        Path,
        typer.Option("--image-path", help="Image path"),
    ],
    colors_path: Annotated[
        Path,
        typer.Option("--colors-path", help="Colors path"),
    ],
) -> None:
    typer.echo(f"Starting color picker with image path: {image_path}")
    color_picker = ColorPicker(image_path=image_path, colors_path=colors_path)
    color_picker.run()
if __name__ == "__main__":
    app()
