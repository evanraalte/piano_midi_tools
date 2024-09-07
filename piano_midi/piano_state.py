from __future__ import annotations

import copy
from typing import Annotated

from pydantic import BaseModel, Field

from piano_midi.models import BlackKeyIndex, Hand, KeyIndex, WhiteKeyIndex


class PianoChanges(BaseModel):
    pressed: set[PianoPress]
    released: set[PianoPress]


class PianoPress(BaseModel):
    index: Annotated[int, Field(strict=True, ge=0, lt=88)]
    hand: Hand | None

    def __hash__(self) -> int:
        return hash((self.index, self.hand))


class PianoState:
    def copy(self) -> PianoState:
        return copy.deepcopy(self)

    def __init__(self) -> None:
        self.state: set[PianoPress] = set()

    def _set_key(self, key_index: KeyIndex, *, is_pressed: bool, hand: Hand) -> None:
        state_changed = False

        # Key is currently not pressed and is being pressed
        piano_press = PianoPress(index=key_index.value, hand=hand)
        if is_pressed and piano_press not in self.state:
            self.state.add(PianoPress(index=key_index.value, hand=hand))
            state_changed = True
        # Key is currently pressed by hand X and is being released by hand X
        elif not is_pressed and piano_press in self.state:
            self.state.remove(PianoPress(index=key_index.value, hand=hand))
            state_changed = True

        if state_changed:
            text = "pressed" if is_pressed else "released"
            print(f"key {key_index.value} is {text} by {hand}")

    def set_white_key(
        self, white_key_idx: int, *, is_pressed: bool, hand: Hand
    ) -> None:
        key_index = WhiteKeyIndex(value=white_key_idx).to_key_index()
        self._set_key(key_index, is_pressed=is_pressed, hand=hand)

    def set_black_key(
        self, black_key_idx: int, *, is_pressed: bool, hand: Hand
    ) -> None:
        key_index = BlackKeyIndex(value=black_key_idx).to_key_index()
        self._set_key(key_index, is_pressed=is_pressed, hand=hand)

    def detect_changes(self, old_state: PianoState) -> PianoChanges:
        # find what is present in current state but not in old state
        pressed = self.state - old_state.state
        # find what is present in old state but not in current state
        released = old_state.state - self.state
        return PianoChanges(pressed=pressed, released=released)
