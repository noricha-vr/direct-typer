"""Main DirectTyper implementation with hybrid typing approach."""

import time
from enum import Enum
from typing import Optional

import pyperclip
from pynput.keyboard import Controller, Key

from direct_typer.cgevent import type_unicode_string


class TypingMethod(Enum):
    """Available typing methods."""

    AUTO = "auto"
    CGEVENT = "cgevent"
    PYNPUT = "pynput"
    CLIPBOARD = "clipboard"


class DirectTyper:
    """Hybrid text typer for macOS.

    Automatically selects the optimal typing method based on text content:
    - Short ASCII text: pynput (fastest)
    - Medium length Unicode: CGEvent (reliable for Unicode)
    - Long text: Clipboard with restore (most reliable)
    """

    # Thresholds for method selection
    ASCII_THRESHOLD = 50
    CGEVENT_THRESHOLD = 200

    def __init__(
        self,
        delay_ms: float = 5,
        default_method: TypingMethod = TypingMethod.AUTO,
    ):
        """Initialize DirectTyper.

        Args:
            delay_ms: Default delay between characters in milliseconds.
            default_method: Default typing method to use.
        """
        self.delay_ms = delay_ms
        self.default_method = default_method
        self._keyboard = Controller()

    def type(self, text: str, method: Optional[TypingMethod] = None) -> None:
        """Type text using the specified or auto-selected method.

        Args:
            text: Text to type.
            method: Typing method to use. If None, uses default_method.
        """
        if not text:
            return

        method = method or self.default_method

        if method == TypingMethod.AUTO:
            self._smart_type(text)
        elif method == TypingMethod.CGEVENT:
            self.type_cgevent(text)
        elif method == TypingMethod.PYNPUT:
            self.type_pynput(text)
        elif method == TypingMethod.CLIPBOARD:
            self.type_clipboard(text)

    def _smart_type(self, text: str) -> None:
        """Automatically select and use the best typing method.

        Selection criteria:
        - Short ASCII (< 50 chars): pynput (fastest)
        - Medium length (< 200 chars): CGEvent Unicode
        - Long text (>= 200 chars): Clipboard with restore

        Args:
            text: Text to type.
        """
        is_ascii = text.isascii()
        length = len(text)

        if is_ascii and length < self.ASCII_THRESHOLD:
            # Short ASCII: use pynput for speed
            self.type_pynput(text)
        elif length < self.CGEVENT_THRESHOLD:
            # Medium length: use CGEvent for Unicode support
            self.type_cgevent(text)
        else:
            # Long text: use clipboard for reliability
            self.type_clipboard(text)

    def type_cgevent(self, text: str) -> None:
        """Type text using CGEvent Unicode method.

        Works with any Unicode character including Japanese, Chinese,
        emoji, etc. Each character is sent as a keyboard event.

        Args:
            text: Text to type.
        """
        type_unicode_string(text, delay_ms=self.delay_ms)

    def type_pynput(self, text: str) -> None:
        """Type text using pynput.

        Fast but may have issues with non-ASCII characters.
        Best for short ASCII text.

        Args:
            text: Text to type.
        """
        for char in text:
            if char == "\n":
                self._keyboard.press(Key.enter)
                self._keyboard.release(Key.enter)
            elif char == "\t":
                self._keyboard.press(Key.tab)
                self._keyboard.release(Key.tab)
            else:
                self._keyboard.type(char)
            if self.delay_ms > 0:
                time.sleep(self.delay_ms / 1000.0)

    def type_clipboard(self, text: str, restore: bool = True) -> None:
        """Type text via clipboard paste with optional restore.

        Most reliable method for long text. Optionally preserves
        the original clipboard content.

        Args:
            text: Text to type.
            restore: Whether to restore original clipboard content.
        """
        original = None
        if restore:
            try:
                original = pyperclip.paste()
            except Exception:
                # Clipboard might be empty or contain non-text data
                original = None

        try:
            pyperclip.copy(text)
            time.sleep(0.05)  # Wait for clipboard to update

            # Cmd+V to paste
            self._keyboard.press(Key.cmd)
            self._keyboard.press("v")
            self._keyboard.release("v")
            self._keyboard.release(Key.cmd)

            time.sleep(0.1)  # Wait for paste to complete
        finally:
            if restore and original is not None:
                try:
                    time.sleep(0.05)
                    pyperclip.copy(original)
                except Exception:
                    pass  # Best effort restore

    def type_with_delay(self, text: str, delay_ms: float) -> None:
        """Type text with a custom delay between characters.

        Args:
            text: Text to type.
            delay_ms: Delay between characters in milliseconds.
        """
        original_delay = self.delay_ms
        self.delay_ms = delay_ms
        try:
            self.type(text)
        finally:
            self.delay_ms = original_delay
