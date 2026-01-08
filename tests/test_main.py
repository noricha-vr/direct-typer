"""Tests for main module (VoiceCodeApp)."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pynput import keyboard

from direct_typer.main import _parse_hotkey, _format_hotkey, VoiceCodeApp
from direct_typer.typer import TypingMethod


class TestParseHotkey:
    """Test _parse_hotkey function."""

    def test_single_function_key(self):
        """Test parsing single function key."""
        keys = _parse_hotkey("f15")
        assert keyboard.Key.f15 in keys

    def test_function_key_uppercase(self):
        """Test parsing uppercase function key."""
        keys = _parse_hotkey("F15")
        assert keyboard.Key.f15 in keys

    def test_modifier_plus_key(self):
        """Test parsing modifier + key combination."""
        keys = _parse_hotkey("ctrl+shift+r")
        assert keyboard.Key.ctrl in keys
        assert keyboard.Key.shift in keys
        # Check for 'r' keycode
        found_r = any(
            isinstance(k, keyboard.KeyCode) and k.char == "r" for k in keys
        )
        assert found_r

    def test_all_modifiers(self):
        """Test parsing all modifier keys."""
        keys = _parse_hotkey("ctrl+shift+alt+cmd+a")
        assert keyboard.Key.ctrl in keys
        assert keyboard.Key.shift in keys
        assert keyboard.Key.alt in keys
        assert keyboard.Key.cmd in keys

    def test_invalid_function_key_raises(self):
        """Test that invalid function key raises ValueError."""
        with pytest.raises(ValueError):
            _parse_hotkey("f99")

    def test_unknown_key_raises(self):
        """Test that unknown key raises ValueError."""
        with pytest.raises(ValueError):
            _parse_hotkey("unknown_key")

    def test_empty_string_raises(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            _parse_hotkey("")

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        keys = _parse_hotkey("  ctrl + shift + f1  ")
        assert keyboard.Key.ctrl in keys
        assert keyboard.Key.shift in keys
        assert keyboard.Key.f1 in keys


class TestFormatHotkey:
    """Test _format_hotkey function."""

    def test_single_function_key(self):
        """Test formatting single function key."""
        keys = {keyboard.Key.f15}
        result = _format_hotkey(keys)
        assert result == "F15"

    def test_modifier_order(self):
        """Test that modifiers are ordered correctly."""
        keys = {
            keyboard.Key.shift,
            keyboard.Key.ctrl,
            keyboard.Key.alt,
            keyboard.Key.cmd,
        }
        result = _format_hotkey(keys)
        # Should be in order: Ctrl, Shift, Alt, Cmd
        assert result == "Ctrl+Shift+Alt+Cmd"

    def test_modifier_plus_function_key(self):
        """Test formatting modifier + function key."""
        keys = {keyboard.Key.ctrl, keyboard.Key.f1}
        result = _format_hotkey(keys)
        assert "Ctrl" in result
        assert "F1" in result

    def test_character_key(self):
        """Test formatting character key."""
        keys = {keyboard.KeyCode.from_char("r")}
        result = _format_hotkey(keys)
        assert result == "R"


class TestVoiceCodeAppInit:
    """Test VoiceCodeApp initialization."""

    @patch("direct_typer.main.rumps.App.__init__")
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch("os.getenv")
    def test_initialization(
        self,
        mock_getenv,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
    ):
        """Test VoiceCodeApp initialization."""
        mock_getenv.return_value = "f15"
        mock_app_init.return_value = None

        app = VoiceCodeApp()

        mock_load_dotenv.assert_called_once()
        mock_recorder.assert_called_once()
        mock_transcriber.assert_called_once()
        mock_postprocessor.assert_called_once()
        # Verify DirectTyper is initialized with CLIPBOARD method for reliability
        mock_typer_class.assert_called_once_with(default_method=TypingMethod.CLIPBOARD)
        mock_start_listener.assert_called_once()


class TestVoiceCodeAppMethods:
    """Test VoiceCodeApp methods."""

    @patch("direct_typer.main.subprocess.Popen")
    @patch("direct_typer.main.rumps.App.__init__", return_value=None)
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch("os.getenv", return_value="f15")
    def test_play_sound(
        self,
        mock_getenv,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
        mock_popen,
    ):
        """Test _play_sound method."""
        app = VoiceCodeApp()
        app._play_sound("/path/to/sound.aiff")

        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert call_args[0][0] == ["afplay", "/path/to/sound.aiff"]

    @patch("direct_typer.main.rumps.App.__init__", return_value=None)
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch("os.getenv", return_value="f15")
    def test_check_hotkey_true(
        self,
        mock_getenv,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
    ):
        """Test _check_hotkey returns True when hotkey is pressed."""
        app = VoiceCodeApp()
        app._current_keys = {keyboard.Key.f15}

        assert app._check_hotkey() is True

    @patch("direct_typer.main.rumps.App.__init__", return_value=None)
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch("os.getenv", return_value="f15")
    def test_check_hotkey_false(
        self,
        mock_getenv,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
    ):
        """Test _check_hotkey returns False when hotkey is not pressed."""
        app = VoiceCodeApp()
        app._current_keys = set()

        assert app._check_hotkey() is False

    @patch("direct_typer.main.rumps.App.__init__", return_value=None)
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch("os.getenv", return_value="f15")
    def test_normalize_key_keycode(
        self,
        mock_getenv,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
    ):
        """Test _normalize_key normalizes KeyCode to lowercase."""
        app = VoiceCodeApp()
        key = keyboard.KeyCode.from_char("A")
        result = app._normalize_key(key)

        assert isinstance(result, keyboard.KeyCode)
        assert result.char == "a"

    @patch("direct_typer.main.rumps.App.__init__", return_value=None)
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch("os.getenv", return_value="f15")
    def test_normalize_key_special(
        self,
        mock_getenv,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
    ):
        """Test _normalize_key returns Key unchanged."""
        app = VoiceCodeApp()
        key = keyboard.Key.f15
        result = app._normalize_key(key)

        assert result == keyboard.Key.f15


class TestStopAndProcess:
    """Test _stop_and_process method."""

    @patch("direct_typer.main.rumps.App.__init__", return_value=None)
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch.object(VoiceCodeApp, "_play_sound")
    @patch("os.getenv", return_value="f15")
    def test_stop_and_process_uses_direct_typer(
        self,
        mock_getenv,
        mock_play_sound,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
    ):
        """Test that _stop_and_process uses DirectTyper instead of clipboard."""
        # Setup mocks
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True

        mock_recorder_instance = MagicMock()
        mock_recorder_instance.stop.return_value = mock_audio_path
        mock_recorder.return_value = mock_recorder_instance

        mock_transcriber_instance = MagicMock()
        mock_transcriber_instance.transcribe.return_value = "hello world"
        mock_transcriber.return_value = mock_transcriber_instance

        mock_postprocessor_instance = MagicMock()
        mock_postprocessor_instance.process.return_value = "Hello world."
        mock_postprocessor.return_value = mock_postprocessor_instance

        mock_typer_instance = MagicMock()
        mock_typer_class.return_value = mock_typer_instance

        # Create app and run method
        app = VoiceCodeApp()
        app.title = VoiceCodeApp.ICON_RECORDING

        app._stop_and_process()

        # Verify DirectTyper.type was called with processed text
        mock_typer_instance.type.assert_called_once_with("Hello world.")

        # Verify cleanup was called
        mock_audio_path.unlink.assert_called_once()

    @patch("direct_typer.main.rumps.App.__init__", return_value=None)
    @patch("direct_typer.main.load_dotenv")
    @patch("direct_typer.main.AudioRecorder")
    @patch("direct_typer.main.Transcriber")
    @patch("direct_typer.main.PostProcessor")
    @patch("direct_typer.main.DirectTyper")
    @patch.object(VoiceCodeApp, "_start_keyboard_listener")
    @patch.object(VoiceCodeApp, "_play_sound")
    @patch("os.getenv", return_value="f15")
    def test_stop_and_process_empty_transcription(
        self,
        mock_getenv,
        mock_play_sound,
        mock_start_listener,
        mock_typer_class,
        mock_postprocessor,
        mock_transcriber,
        mock_recorder,
        mock_load_dotenv,
        mock_app_init,
    ):
        """Test _stop_and_process handles empty transcription."""
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True

        mock_recorder_instance = MagicMock()
        mock_recorder_instance.stop.return_value = mock_audio_path
        mock_recorder.return_value = mock_recorder_instance

        mock_transcriber_instance = MagicMock()
        mock_transcriber_instance.transcribe.return_value = "   "  # Empty/whitespace
        mock_transcriber.return_value = mock_transcriber_instance

        mock_typer_instance = MagicMock()
        mock_typer_class.return_value = mock_typer_instance

        app = VoiceCodeApp()
        app.title = VoiceCodeApp.ICON_RECORDING

        app._stop_and_process()

        # Verify DirectTyper.type was NOT called
        mock_typer_instance.type.assert_not_called()

        # Verify error sound was played
        mock_play_sound.assert_called_with(VoiceCodeApp.SOUND_ERROR)
