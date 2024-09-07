from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from piano_midi.models import BlackKeyIndex, Hand, KeyIndex, WhiteKeyIndex


class PianoChanges(BaseModel):
    pressed: list[PianoPress]
    released: list[PianoPress]


class PianoPress(BaseModel):
    index: Annotated[int, Field(strict=True, ge=0, lt=88)]
    hand: Hand | None


class PianoKeyState:
    TOTAL_KEYS: int = 88
    WHITE_KEYS: int = 52
    BLACK_KEYS: int = 36

    def __init__(self) -> None:
        self.state: int = 0

    def set_key(self, key_index: KeyIndex, *, is_pressed: bool) -> None:
        if is_pressed:
            self.state |= 1 << key_index.value
        else:
            self.state &= ~(1 << key_index.value)

    def is_key_pressed(self, key_index: KeyIndex) -> bool:
        return bool(self.state & (1 << key_index.value))

    def detect_changes(self, old_state: PianoKeyState) -> tuple[list[int], list[int]]:
        diff = self.state ^ old_state.state
        released = [
            i
            for i in range(self.TOTAL_KEYS)
            if diff & (1 << i) and old_state.state & (1 << i)
        ]
        pressed = [
            i
            for i in range(self.TOTAL_KEYS)
            if diff & (1 << i) and self.state & (1 << i)
        ]
        return pressed, released

    def __repr__(self) -> str:
        pressed_keys = [
            PianoState.index_to_key(i)
            for i in range(self.TOTAL_KEYS)
            if self.is_key_pressed(KeyIndex(value=i))
        ]
        return f"PianoKeyState(pressed_keys={pressed_keys})"


class PianoHandState:
    def __init__(self) -> None:
        self.hand_state: list[Hand | None] = [None] * PianoKeyState.TOTAL_KEYS

    def set_hand(
        self, key_index: KeyIndex, hand: Hand | None, *, is_pressed: bool
    ) -> None:
        self.hand_state[key_index.value] = hand if is_pressed else None

    def get_hand(self, key_index: KeyIndex) -> Hand | None:
        return self.hand_state[key_index.value]

    def __repr__(self) -> str:
        active_hands = [
            f"{PianoState.index_to_key(i)}({self.hand_state[i].name})"  # type: ignore[union-attr]
            for i in range(PianoKeyState.TOTAL_KEYS)
            if self.hand_state[i] is not None
        ]
        return f"PianoHandState(active_hands={active_hands})"


class PianoState:
    def __init__(self, key_state: PianoKeyState, hand_state: PianoHandState) -> None:
        self.key_state = key_state
        self.hand_state = hand_state

    def _set_key(
        self, key_index: KeyIndex, *, is_pressed: bool, hand: Hand | None = None
    ) -> None:
        self.key_state.set_key(key_index, is_pressed=is_pressed)
        self.hand_state.set_hand(key_index, hand, is_pressed=is_pressed)

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

    def is_key_pressed(self, key_index: int) -> bool:
        return self.key_state.is_key_pressed(KeyIndex(value=key_index))

    def get_hand(self, key_index: int) -> Hand | None:
        return self.hand_state.get_hand(KeyIndex(value=key_index))

    def detect_changes(self, other_state: PianoState) -> PianoChanges:
        key_pressed, key_released = self.key_state.detect_changes(other_state.key_state)

        pressed = [
            PianoPress(index=i, hand=other_state.get_hand(i)) for i in key_pressed
        ]
        released = [PianoPress(index=i, hand=self.get_hand(i)) for i in key_released]

        return PianoChanges(pressed=pressed, released=released)

    @staticmethod
    def index_to_key(index: int) -> str:
        if 0 <= index < PianoKeyState.TOTAL_KEYS:
            note_names = [
                "A",
                "A#",
                "B",
                "C",
                "C#",
                "D",
                "D#",
                "E",
                "F",
                "F#",
                "G",
                "G#",
            ]
            octave = (index + 9) // 12
            note = note_names[(index + 9) % 12]
            return f"{note}{octave}"
        msg = f"Invalid key index: {index}"
        raise ValueError(msg)

    def __repr__(self) -> str:
        pressed_keys = [
            f"{self.index_to_key(i)}({self.get_hand(i).name if self.get_hand(i) else 'None'})"  # type: ignore[union-attr]
            for i in range(PianoKeyState.TOTAL_KEYS)
            if self.is_key_pressed(i)
        ]
        return f"CompletePianoState(pressed_keys={pressed_keys})"
