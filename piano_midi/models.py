import numpy as np
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
