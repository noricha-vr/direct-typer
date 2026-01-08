"""CGEvent low-level implementation for Unicode text input on macOS."""

import time
from typing import Optional

from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventKeyboardSetUnicodeString,
    CGEventPost,
    kCGHIDEventTap,
    kCGEventKeyDown,
    kCGEventKeyUp,
    CGEventSetFlags,
)


# Virtual key codes for special characters
SPECIAL_KEYS = {
    "\n": 36,  # Return
    "\r": 36,  # Return
    "\t": 48,  # Tab
}


def type_unicode_char(char: str, delay_ms: float = 0) -> None:
    """Send a single Unicode character as keyboard event.

    Args:
        char: Single character to type.
        delay_ms: Delay after typing in milliseconds.

    Raises:
        ValueError: If char is not exactly one character.
    """
    if len(char) != 1:
        raise ValueError(f"Expected single character, got {len(char)} characters")

    # Handle special keys with virtual key codes
    if char in SPECIAL_KEYS:
        keycode = SPECIAL_KEYS[char]
        event_down = CGEventCreateKeyboardEvent(None, keycode, True)
        event_up = CGEventCreateKeyboardEvent(None, keycode, False)
    else:
        # Use Unicode string for regular characters
        event_down = CGEventCreateKeyboardEvent(None, 0, True)
        CGEventKeyboardSetUnicodeString(event_down, len(char), char)

        event_up = CGEventCreateKeyboardEvent(None, 0, False)
        CGEventKeyboardSetUnicodeString(event_up, len(char), char)

    if event_down is None or event_up is None:
        raise RuntimeError(f"Failed to create keyboard event for character: {char!r}")

    CGEventPost(kCGHIDEventTap, event_down)
    CGEventPost(kCGHIDEventTap, event_up)

    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)


def type_unicode_string(text: str, delay_ms: float = 5) -> None:
    """Send a Unicode string as keyboard events.

    Each character is sent as a separate key down/up event pair.
    This method works with any Unicode character including Japanese,
    Chinese, emoji, etc.

    Args:
        text: Text to type.
        delay_ms: Delay between characters in milliseconds.
    """
    for char in text:
        type_unicode_char(char, delay_ms)


def type_unicode_batch(text: str, batch_size: int = 20, delay_ms: float = 10) -> None:
    """Send Unicode text in batches for better performance.

    For longer texts, this can be more efficient than character-by-character
    typing while still maintaining reliability.

    Args:
        text: Text to type.
        batch_size: Maximum characters per batch.
        delay_ms: Delay between batches in milliseconds.
    """
    for i in range(0, len(text), batch_size):
        batch = text[i : i + batch_size]
        for char in batch:
            type_unicode_char(char, delay_ms=0)
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
