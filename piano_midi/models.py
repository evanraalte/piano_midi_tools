from enum import Enum
from pathlib import Path
from typing import Annotated, Self

import numpy as np
import pydantic
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
        with yaml_path.open("r") as file:
            data = yaml.safe_load(file)
        try:
            return cls.model_validate(data)
        except ValidationError:
            return cls()

    def to_yaml(self, yaml_path: Path) -> None:
        with yaml_path.open("w") as file:
            file.write(yaml.dump(self.model_dump(mode="json")))


class PianoKey(Enum):
    # store number of expected keys
    WHITE = 52
    BLACK = 36


class Hand(Enum):
    LEFT = 0
    RIGHT = 1


class KeyIndex(BaseModel):
    value: Annotated[int, Field(strict=True, ge=0, lt=88)]


class WhiteKeyIndex(BaseModel):
    value: Annotated[int, Field(strict=True, ge=0, lt=52)]

    def to_key_index(self) -> KeyIndex:
        special_case = 51
        octave = self.value // 7
        key_in_octave = self.value % 7
        offsets = [0, 2, 4, 5, 7, 9, 11]

        if self.value == special_case:  # Special case for the highest white key
            return KeyIndex(value=87)

        index = octave * 12 + offsets[key_in_octave]
        return KeyIndex(value=index)


class BlackKeyIndex(BaseModel):
    value: Annotated[int, Field(strict=True, ge=0, lt=36)]

    def to_key_index(self) -> KeyIndex:
        # map the 0-34 range to the 0-87 range
        octave = self.value // 5
        key_in_octave = self.value % 5
        offsets = [1, 3, 6, 8, 10]
        index = octave * 12 + offsets[key_in_octave]
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
    start: int  # in pixels
    end: int  # in pixels


class KeySegments(BaseModelYaml, validate_assignment=True):
    white: list[KeySegment] | None = None
    black: list[KeySegment] | None = None

    @pydantic.model_validator(mode="after")
    def validate_num_keys(self) -> Self:
        expected_white_keys = 52
        if self.white and len(self.white) != expected_white_keys:
            raise InvalidNumOfKeySegmentsError(
                expected_num_keys=expected_white_keys,
                actual_num_keys=len(self.white),
                key_name="white",
            )
        expected_black_keys = 36
        if self.black and len(self.black) != expected_black_keys:
            raise InvalidNumOfKeySegmentsError(
                expected_num_keys=expected_black_keys,
                actual_num_keys=len(self.black),
                key_name="black",
            )
        return self


class KeyColor(Enum):
    LEFT_WHITE = 0
    RIGHT_WHITE = 1
    LEFT_BLACK = 2
    RIGHT_BLACK = 3


class KeyColors(BaseModelYaml):
    left_white: HSVRange | None = None
    right_white: HSVRange | None = None
    left_black: HSVRange | None = None
    right_black: HSVRange | None = None
