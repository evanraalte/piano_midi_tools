from enum import Enum

import numpy as np
from pydantic import BaseModel


class Range(BaseModel):
    min: int
    max: int


class HSVRange(BaseModel):
    """
    Convert to HSV
    HSV Format:
    H: Hue - color type (such as red, blue, or yellow).
       In OpenCV it ranges from 0 to 179.
    S: Saturation - vibrancy of the color (0-255).
       0 is white/gray, 255 is the full color.
    V: Value - brightness of the color (0-255).
       0 is black, 255 is the brightest.
    """

    h: Range
    s: Range
    v: Range

    def lower(self) -> np.ndarray:
        return np.array([self.h.min, self.s.min, self.v.min])

    def upper(self) -> np.ndarray:
        return np.array([self.h.max, self.s.max, self.v.max])


ESC_KEY = 27


class PianoKey(Enum):
    # store number of expected keys
    WHITE = 52
    BLACK = 36
