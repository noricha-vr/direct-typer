#!/usr/bin/env python3
"""Demo script for direct-typer.

This script demonstrates different typing methods.
Run it and click on a text editor to see the output.

Usage:
    uv run python examples/demo.py
"""

import time
import sys

from direct_typer import DirectTyper
from direct_typer.typer import TypingMethod


def wait_for_focus(seconds: int = 3) -> None:
    """Wait for user to focus on target window."""
    print(f"You have {seconds} seconds to click on a text editor...")
    for i in range(seconds, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("Typing!")


def demo_basic():
    """Basic typing demonstration."""
    print("\n=== Basic Typing Demo ===")
    print("This demo will type text using automatic method selection.")

    typer = DirectTyper()
    wait_for_focus()

    # ASCII text (will use pynput)
    typer.type("Hello, World!\n")
    time.sleep(0.5)

    # Japanese text (will use CGEvent)
    typer.type("こんにちは、世界！\n")
    time.sleep(0.5)

    # Mixed content
    typer.type("Python 3.13 + 日本語 = OK\n")


def demo_methods():
    """Demonstrate different typing methods."""
    print("\n=== Typing Methods Demo ===")
    print("This demo will show each typing method.")

    typer = DirectTyper()
    wait_for_focus()

    # CGEvent method
    print("Using CGEvent...")
    typer.type("CGEvent: ", method=TypingMethod.CGEVENT)
    typer.type("日本語テスト\n", method=TypingMethod.CGEVENT)
    time.sleep(0.5)

    # pynput method
    print("Using pynput...")
    typer.type("pynput: ", method=TypingMethod.PYNPUT)
    typer.type("ASCII only\n", method=TypingMethod.PYNPUT)
    time.sleep(0.5)

    # Clipboard method
    print("Using clipboard...")
    typer.type("Clipboard: ", method=TypingMethod.CLIPBOARD)
    typer.type("クリップボード経由\n", method=TypingMethod.CLIPBOARD)


def demo_special_chars():
    """Demonstrate special character handling."""
    print("\n=== Special Characters Demo ===")
    print("This demo will type special characters.")

    typer = DirectTyper()
    wait_for_focus()

    typer.type("Line 1\n")
    typer.type("Line 2\n")
    typer.type("Tab:\tafter tab\n")
    typer.type("Symbols: @#$%^&*()_+-=[]{}|;':\",./<>?\n")


def demo_unicode():
    """Demonstrate Unicode support."""
    print("\n=== Unicode Demo ===")
    print("This demo will type various Unicode characters.")

    typer = DirectTyper()
    wait_for_focus()

    texts = [
        "English: Hello, World!",
        "Japanese: こんにちは、世界！",
        "Chinese: 你好，世界！",
        "Korean: 안녕하세요, 세계!",
        "Russian: Привет, мир!",
        "Arabic: مرحبا بالعالم",
        "Emoji: This is a test",  # Emojis removed as per guidelines
        "Math: ∑∏∫∂√∞≠≤≥",
    ]

    for text in texts:
        typer.type(text + "\n")
        time.sleep(0.3)


def main():
    """Run demos."""
    print("Direct Typer Demo")
    print("=" * 40)
    print("\nThis demo requires accessibility permissions.")
    print("Enable: System Settings > Privacy & Security > Accessibility")
    print("\nAvailable demos:")
    print("  1. Basic typing (auto method selection)")
    print("  2. Different typing methods")
    print("  3. Special characters")
    print("  4. Unicode support")
    print("  5. Run all demos")
    print("  q. Quit")

    while True:
        choice = input("\nSelect demo (1-5, q): ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break
        elif choice == "1":
            demo_basic()
        elif choice == "2":
            demo_methods()
        elif choice == "3":
            demo_special_chars()
        elif choice == "4":
            demo_unicode()
        elif choice == "5":
            demo_basic()
            demo_methods()
            demo_special_chars()
            demo_unicode()
        else:
            print("Invalid choice. Please enter 1-5 or q.")


if __name__ == "__main__":
    main()
