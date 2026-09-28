#!/usr/bin/env python3
"""
AI Text Humanizer CLI

A clean command-line interface for humanizing AI-generated text.

Features:
- Interactive mode
- File input/output
- Local or OpenAI processing
- Low / Medium / High strength
- Original vs. humanized comparison
- Statistics
- Environment-variable API key support
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from humanizer import humanize_text


# ─────────────────────────────────────────────────────────────
# Terminal Colors
# ─────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"

PURPLE = "\033[95m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"


# ─────────────────────────────────────────────────────────────
# Terminal Helpers
# ─────────────────────────────────────────────────────────────

def color(text: str, colour: str) -> str:
    """Return colored text."""
    return f"{colour}{text}{RESET}"


def clear_console() -> None:
    """Clear the terminal screen."""
    command = "cls" if os.name == "nt" else "clear"
    os.system(command)


def print_banner() -> None:
    """Display the application banner."""
    print()
    print(color("=" * 64, PURPLE))
    print(color("                ✨ AI TEXT HUMANIZER ✨", PURPLE + BOLD))
    print(color("          Transform AI text into natural writing", CYAN))
    print(color("=" * 64, PURPLE))
    print()


def print_error(message: str) -> None:
    """Display an error message."""
    print(f"\n{color('✗ ' + message, RED)}")


def print_warning(message: str) -> None:
    """Display a warning message."""
    print(f"\n{color('⚠ ' + message, YELLOW)}")


def print_success(message: str) -> None:
    """Display a success message."""
    print(f"\n{color('✔ ' + message, GREEN)}")


# ─────────────────────────────────────────────────────────────
# File Operations
# ─────────────────────────────────────────────────────────────

def read_file(filepath: str) -> str:
    """
    Read UTF-8 text from a file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        OSError: If the file cannot be read.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    if not path.is_file():
        raise OSError(f"Input path is not a file: {filepath}")

    return path.read_text(encoding="utf-8")


def save_to_file(text: str, filepath: str) -> bool:
    """
    Save text to a UTF-8 file.

    Creates parent directories automatically.
    """
    try:
        path = Path(filepath)

        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(text, encoding="utf-8")

        print_success(f"Successfully exported to: {path}")
        return True

    except OSError as exc:
        print_error(f"Could not save file: {exc}")
        return False


# ─────────────────────────────────────────────────────────────
# Text Statistics
# ─────────────────────────────────────────────────────────────

def get_text_stats(text: str) -> tuple[int, int]:
    """Return word count and character count."""
    words = len(text.split())
    characters = len(text)
    return words, characters


def display_comparison(original: str, humanized: str) -> None:
    """Display original text, humanized text, and statistics."""

    original_words, original_chars = get_text_stats(original)
    humanized_words, humanized_chars = get_text_stats(humanized)

    if original_words:
        word_change = (
            (humanized_words - original_words)
            / original_words
        ) * 100
    else:
        word_change = 0.0

    print()
    print(color("=" * 64, BLUE))
    print(
        color(
            f"--- ORIGINAL TEXT --- "
            f"({original_words} words, {original_chars} chars)",
            BLUE + BOLD,
        )
    )
    print(color("-" * 64, BLUE))
    print(original.strip())

    print()
    print(color("=" * 64, GREEN))
    print(
        color(
            f"--- HUMANIZED TEXT --- "
            f"({humanized_words} words, {humanized_chars} chars)",
            GREEN + BOLD,
        )
    )
    print(color("-" * 64, GREEN))
    print(humanized.strip())

    print(color("=" * 64, GREEN))

    print()
    print(color("Statistics", BOLD))

    change_symbol = "↑" if word_change > 0 else "↓" if word_change < 0 else "→"

    print(
        f" • Words: "
        f"{original_words} → {humanized_words} "
        f"({word_change:+.1f}%) {change_symbol}"
    )

    print(
        f" • Characters: "
        f"{original_chars} → {humanized_chars}"
    )


# ─────────────────────────────────────────────────────────────
# User Input
# ─────────────────────────────────────────────────────────────

def read_multiline_input() -> Optional[str]:
    """
    Read multiline text from the terminal.

    Press:
        Ctrl+D on Linux/macOS
        Ctrl+Z followed by Enter on Windows
    """
    print(color("Enter the AI-generated text:", BOLD))
    print(
        color(
            "(Finish with Ctrl+D on Linux/macOS "
            "or Ctrl+Z + Enter on Windows.)",
            BLUE,
        )
    )
    print()

    lines: list[str] = []

    while True:
        try:
            lines.append(input())
        except EOFError:
            break
        except KeyboardInterrupt:
            print_warning("Input cancelled.")
            return None

    text = "\n".join(lines)

    if not text.strip():
        print_warning("Input is empty.")
        return None

    return text


def choose_strength() -> str:
    """Ask the user to select humanization strength."""

    print(color("Select Humanization Strength:", BOLD))
    print(" [1] Low    - Minimal changes")
    print(" [2] Medium - Balanced changes")
    print(" [3] High   - Strong conversational changes")

    choice = input(
        "\nChoose [1-3] "
        f"{color('(default: 2)', BLUE)}: "
    ).strip()

    return {
        "1": "Low",
        "3": "High",
    }.get(choice, "Medium")


def choose_method() -> tuple[str, Optional[str]]:
    """
    Ask the user to choose the processing method.

    Returns:
        (method, api_key)
    """

    print()
    print(color("Select Humanization Method:", BOLD))
    print(" [1] Local  - Fast and offline")
    print(" [2] OpenAI - AI-powered processing")

    choice = input(
        "\nChoose [1-2] "
        f"{color('(default: 1)', BLUE)}: "
    ).strip()

    if choice != "2":
        return "local", None

    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print_success("Using OPENAI_API_KEY from environment.")
        return "openai", api_key

    print()
    api_key = input("Enter your OpenAI API Key: ").strip()

    if not api_key:
        print_warning(
            "No API key provided. Falling back to local engine."
        )
        return "local", None

    return "openai", api_key


# ─────────────────────────────────────────────────────────────
# Humanization
# ─────────────────────────────────────────────────────────────

def process_text(
    text: str,
    strength: str,
    method: str,
    api_key: Optional[str] = None,
) -> str:
    """Humanize text using the selected engine."""

    print()
    print(
        f"⌛ Processing with "
        f"{color(method.upper(), BOLD)} engine "
        f"(Strength: {color(strength, BOLD)})..."
    )

    return humanize_text(
        text,
        strength=strength,
        method=method,
        openai_api_key=api_key,
    )


# ─────────────────────────────────────────────────────────────
# Interactive Mode
# ─────────────────────────────────────────────────────────────

def run_interactive() -> None:
    """Run the interactive CLI."""

    clear_console()
    print_banner()

    text = read_multiline_input()

    if not text:
        return

    strength = choose_strength()
    method, api_key = choose_method()

    try:
        humanized = process_text(
            text=text,
            strength=strength,
            method=method,
            api_key=api_key,
        )

        display_comparison(text, humanized)

        print()
        export = input(
            "Export humanized text to a file? [y/N]: "
        ).strip().lower()

        if export == "y":
            filepath = input(
                "Output path "
                f"{color('(default: humanized_text.txt)', BLUE)}: "
            ).strip()

            filepath = filepath or "humanized_text.txt"
            save_to_file(humanized, filepath)

    except Exception as exc:
        print_error(f"Humanization failed: {exc}")
        return

    print()
    print_success("Thank you for using AI Text Humanizer!")
    print()


# ─────────────────────────────────────────────────────────────
# Argument Parser
# ─────────────────────────────────────────────────────────────

def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="humanizer",
        description=(
            "Transform AI-generated text into more natural-sounding text."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input",
        help="Path to the input text file.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path where the humanized text should be saved.",
    )

    parser.add_argument(
        "-s",
        "--strength",
        choices=["Low", "Medium", "High"],
        default="Medium",
        help="Humanization strength.",
    )

    parser.add_argument(
        "-m",
        "--method",
        choices=["local", "openai"],
        default="local",
        help="Processing engine.",
    )

    parser.add_argument(
        "-k",
        "--key",
        help=(
            "OpenAI API key. "
            "If omitted, OPENAI_API_KEY will be used."
        ),
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored terminal output.",
    )

    return parser


# ─────────────────────────────────────────────────────────────
# CLI Mode
# ─────────────────────────────────────────────────────────────

def run_cli(args: argparse.Namespace) -> int:
    """Run the non-interactive CLI mode."""

    try:
        # ── Read input ────────────────────────────────────────
        if args.input:
            text = read_file(args.input)
        else:
            print(
                color(
                    "Reading from standard input... "
                    "(Ctrl+D / Ctrl+Z to finish)",
                    BLUE,
                )
            )
            text = sys.stdin.read()

        if not text.strip():
            print_warning("Input is empty. Nothing to humanize.")
            return 0

        # ── API key ──────────────────────────────────────────
        api_key = args.key or os.getenv("OPENAI_API_KEY")

        if args.method == "openai" and not api_key:
            print_error(
                "OpenAI method selected, but no API key was provided.\n"
                "Use --key or set the OPENAI_API_KEY environment variable."
            )
            return 1

        # ── Process ─────────────────────────────────────────
        humanized = process_text(
            text=text,
            strength=args.strength,
            method=args.method,
            api_key=api_key,
        )

        # ── Output ──────────────────────────────────────────
        if args.output:
            return 0 if save_to_file(
                humanized,
                args.output,
            ) else 1

        display_comparison(text, humanized)
        return 0

    except FileNotFoundError as exc:
        print_error(str(exc))
        return 1

    except OSError as exc:
        print_error(f"File error: {exc}")
        return 1

    except KeyboardInterrupt:
        print_warning("Operation cancelled by user.")
        return 130

    except Exception as exc:
        print_error(f"Error: {exc}")
        return 1


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main() -> int:
    """Application entry point."""

    parser = create_parser()

    # No arguments → interactive mode
    if len(sys.argv) == 1:
        run_interactive()
        return 0

    args = parser.parse_args()

    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
