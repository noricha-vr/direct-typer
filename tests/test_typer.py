"""Tests for DirectTyper."""

import pytest
from unittest.mock import MagicMock, patch, call

from direct_typer import DirectTyper
from direct_typer.typer import TypingMethod


class TestDirectTyperInit:
    """Test DirectTyper initialization."""

    def test_default_initialization(self):
        """Test default initialization values."""
        typer = DirectTyper()
        assert typer.delay_ms == 5
        assert typer.default_method == TypingMethod.AUTO

    def test_custom_initialization(self):
        """Test custom initialization values."""
        typer = DirectTyper(delay_ms=10, default_method=TypingMethod.CGEVENT)
        assert typer.delay_ms == 10
        assert typer.default_method == TypingMethod.CGEVENT


class TestSmartType:
    """Test automatic method selection."""

    @patch.object(DirectTyper, "type_pynput")
    def test_short_ascii_uses_pynput(self, mock_pynput):
        """Short ASCII text should use pynput."""
        typer = DirectTyper()
        typer.type("Hello")
        mock_pynput.assert_called_once_with("Hello")

    @patch.object(DirectTyper, "type_cgevent")
    def test_unicode_uses_cgevent(self, mock_cgevent):
        """Unicode text should use CGEvent."""
        typer = DirectTyper()
        typer.type("こんにちは")
        mock_cgevent.assert_called_once_with("こんにちは")

    @patch.object(DirectTyper, "type_cgevent")
    def test_medium_ascii_uses_cgevent(self, mock_cgevent):
        """Medium length ASCII should use CGEvent."""
        typer = DirectTyper()
        text = "a" * 60  # Over ASCII_THRESHOLD
        typer.type(text)
        mock_cgevent.assert_called_once_with(text)

    @patch.object(DirectTyper, "type_clipboard")
    def test_long_text_uses_clipboard(self, mock_clipboard):
        """Long text should use clipboard."""
        typer = DirectTyper()
        text = "a" * 250  # Over CGEVENT_THRESHOLD
        typer.type(text)
        mock_clipboard.assert_called_once_with(text)


class TestMethodSelection:
    """Test explicit method selection."""

    @patch.object(DirectTyper, "type_pynput")
    def test_explicit_pynput(self, mock_pynput):
        """Explicit pynput method should be used."""
        typer = DirectTyper()
        typer.type("test", method=TypingMethod.PYNPUT)
        mock_pynput.assert_called_once_with("test")

    @patch.object(DirectTyper, "type_cgevent")
    def test_explicit_cgevent(self, mock_cgevent):
        """Explicit CGEvent method should be used."""
        typer = DirectTyper()
        typer.type("test", method=TypingMethod.CGEVENT)
        mock_cgevent.assert_called_once_with("test")

    @patch.object(DirectTyper, "type_clipboard")
    def test_explicit_clipboard(self, mock_clipboard):
        """Explicit clipboard method should be used."""
        typer = DirectTyper()
        typer.type("test", method=TypingMethod.CLIPBOARD)
        mock_clipboard.assert_called_once_with("test")


class TestEmptyInput:
    """Test empty input handling."""

    @patch.object(DirectTyper, "type_pynput")
    @patch.object(DirectTyper, "type_cgevent")
    @patch.object(DirectTyper, "type_clipboard")
    def test_empty_string_does_nothing(
        self, mock_clipboard, mock_cgevent, mock_pynput
    ):
        """Empty string should not call any typing method."""
        typer = DirectTyper()
        typer.type("")
        mock_pynput.assert_not_called()
        mock_cgevent.assert_not_called()
        mock_clipboard.assert_not_called()


class TestTypePynput:
    """Test pynput typing method."""

    @patch("direct_typer.typer.Controller")
    def test_type_regular_chars(self, mock_controller_class):
        """Test typing regular characters."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard

        typer = DirectTyper(delay_ms=0)
        typer.type_pynput("ab")

        assert mock_keyboard.type.call_count == 2
        mock_keyboard.type.assert_any_call("a")
        mock_keyboard.type.assert_any_call("b")

    @patch("direct_typer.typer.Controller")
    def test_type_newline(self, mock_controller_class):
        """Test typing newline character."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard

        typer = DirectTyper(delay_ms=0)
        typer.type_pynput("\n")

        mock_keyboard.press.assert_called()
        mock_keyboard.release.assert_called()

    @patch("direct_typer.typer.Controller")
    def test_type_tab(self, mock_controller_class):
        """Test typing tab character."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard

        typer = DirectTyper(delay_ms=0)
        typer.type_pynput("\t")

        mock_keyboard.press.assert_called()
        mock_keyboard.release.assert_called()


class TestTypeClipboard:
    """Test clipboard typing method."""

    @patch("direct_typer.typer.pyperclip")
    @patch("direct_typer.typer.Controller")
    def test_clipboard_restore(self, mock_controller_class, mock_pyperclip):
        """Test clipboard content is restored."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard
        mock_pyperclip.paste.return_value = "original"

        typer = DirectTyper()
        typer.type_clipboard("new text", restore=True)

        # Verify paste was called to get original
        mock_pyperclip.paste.assert_called()
        # Verify copy was called twice (new text, then restore)
        assert mock_pyperclip.copy.call_count == 2
        mock_pyperclip.copy.assert_any_call("new text")
        mock_pyperclip.copy.assert_any_call("original")

    @patch("direct_typer.typer.pyperclip")
    @patch("direct_typer.typer.Controller")
    def test_clipboard_no_restore(self, mock_controller_class, mock_pyperclip):
        """Test clipboard without restore."""
        mock_keyboard = MagicMock()
        mock_controller_class.return_value = mock_keyboard

        typer = DirectTyper()
        typer.type_clipboard("new text", restore=False)

        # Verify paste was not called
        mock_pyperclip.paste.assert_not_called()
        # Verify copy was called once
        mock_pyperclip.copy.assert_called_once_with("new text")


class TestTypeWithDelay:
    """Test custom delay typing."""

    @patch.object(DirectTyper, "type")
    def test_custom_delay_restored(self, mock_type):
        """Test that original delay is restored after typing."""
        typer = DirectTyper(delay_ms=5)
        typer.type_with_delay("test", delay_ms=20)

        assert typer.delay_ms == 5  # Original delay restored


class TestCGEventModule:
    """Test CGEvent module functions."""

    def test_type_unicode_char_invalid_input(self):
        """Test that invalid input raises ValueError."""
        from direct_typer.cgevent import type_unicode_char

        with pytest.raises(ValueError):
            type_unicode_char("ab")  # More than one character

        with pytest.raises(ValueError):
            type_unicode_char("")  # Empty string
