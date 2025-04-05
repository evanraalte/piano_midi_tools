from enum import Enum, auto
from pathlib import Path
from typing import Annotated, Self

import numpy as np
import yaml
from pydantic import BaseModel, Field, ValidationError


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


class BaseModelYaml(BaseModel):
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> Self:
        if not yaml_path.exists():
            yaml_path.touch()
        with yaml_path.open("r") as file:
            data = yaml.safe_load(file)
        try:
            return cls.model_validate(data)
        except ValidationError:
            return cls()

    def to_yaml(self, yaml_path: Path) -> None:
        with yaml_path.open("w") as file:
            file.write(yaml.dump(self.model_dump(mode="json")))


class PianoKeyColor(Enum):
    # store number of expected keys
    WHITE = auto()
    BLACK = auto()


class Hand(Enum):
    LEFT = auto()
    RIGHT = auto()


class KeyIndex(BaseModel):
    value: Annotated[int, Field(strict=True, ge=0, lt=88)]

    def is_white(self) -> bool:
        return self.value % 12 in {0, 2, 4, 5, 7, 9, 11}

    def is_black(self) -> bool:
        return self.value % 12 in {1, 3, 6, 8, 10}

    @classmethod
    def from_white_key_index(
        cls, white_key_index: Annotated[int, Field(strict=True, ge=0, lt=52)]
    ) -> Self:
        octave = white_key_index // 7
        lut: dict[int, int] = {
            0: 0,
            1: 2,
            2: 3,
            3: 5,
            4: 7,
            5: 8,
            6: 10,
        }
        key = white_key_index - octave * 7
        index = lut[key] + octave * 12
        return KeyIndex(value=index)

    @classmethod
    def from_black_key_index(
        cls, black_key_index: Annotated[int, Field(strict=True, ge=0, lt=36)]
    ) -> Self:
        octave = black_key_index // 5
        lut: dict[int, int] = {
            0: 1,
            1: 4,
            2: 6,
            3: 9,
            4: 11,
        }
        key = black_key_index - octave * 5
        index = lut[key] + octave * 12
        return KeyIndex(value=index)


class InvalidNumOfKeySegmentsError(Exception):
    def __init__(
        self, expected_num_keys: int, actual_num_keys: int, key_name: str
    ) -> None:
        self.expected_keys = expected_num_keys
        self.actual_keys = actual_num_keys
        msg = f"Did not detect {expected_num_keys} {key_name} keys, instead got {actual_num_keys}"
        super().__init__(msg)


class KeySegment(BaseModel):
    start_px: int
    end_px: int


class KeySegments(BaseModelYaml, validate_assignment=True):
    white: list[KeySegment] | None = None
    black: list[KeySegment] | None = None


KeyColorIndex = tuple[PianoKeyColor, Hand]


class KeyColors(BaseModelYaml):
    colors: dict[tuple[PianoKeyColor, Hand], HSVRange] = Field(default_factory=dict)
