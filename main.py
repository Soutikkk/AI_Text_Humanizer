#!/usr/bin/env python3
"""
AI Text Humanizer CLI
Provides a clean, interactive command-line interface to humanize AI text.
Supports file input/output, strength settings, and comparison views.
"""

import sys
import os
import argparse
from humanizer import humanize_text

# ANSI color codes for premium terminal feedback
COLOR_HEADER = "\033[95m"
COLOR_BLUE = "\033[94m"
COLOR_GREEN = "\033[92m"
COLOR_WARNING = "\033[93m"
COLOR_FAIL = "\033[91m"
COLOR_END = "\033[0m"
COLOR_BOLD = "\033[1m"


def clear_console():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    """Prints the application banner."""
    print(f"{COLOR_HEADER}{COLOR_BOLD}")
    print("=" * 60)
    print("              ✨ AI TEXT HUMANIZER CLI ✨")
    print("       Transform rigid AI content into natural flow")
    print("=" * 60)
    print(f"{COLOR_END}")


def save_to_file(text, filepath):
    """Saves text to a file, handling directories and errors gracefully."""
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n{COLOR_GREEN}✔ Successfully exported to: {filepath}{COLOR_END}")
        return True
    except Exception as e:
        print(f"\n{COLOR_FAIL}✗ Error exporting file: {e}{COLOR_FAIL}")
        return False


def display_comparison(original, humanized):
    """Displays original and humanized text side-by-side or stacked, with stats."""
    orig_words = len(original.split())
    orig_chars = len(original)
    hum_words = len(humanized.split())
    hum_chars = len(humanized)

    print("\n" + "=" * 60)
    print(f"{COLOR_BLUE}{COLOR_BOLD}--- ORIGINAL TEXT ---{COLOR_END} ({orig_words} words, {orig_chars} chars)")
    print(original.strip())
    print("\n" + "=" * 60)
    print(f"{COLOR_GREEN}{COLOR_BOLD}--- HUMANIZED TEXT ---{COLOR_END} ({hum_words} words, {hum_chars} chars)")
    print(humanized.strip())
    print("=" * 60)

    # Compute a quick similarity heuristic or word reduction/addition stat
    diff_pct = ((hum_words - orig_words) / orig_words) * 100 if orig_words > 0 else 0
    print(f"\n{COLOR_BOLD}Statistics Summary:{COLOR_END}")
    print(f" • Word Count Change: {orig_words} ➔ {hum_words} ({diff_pct:+.1f}%)")
    print(f" • Char Count Change: {orig_chars} ➔ {hum_chars}")


def run_interactive():
    """Runs the interactive CLI mode."""
    clear_console()
    print_banner()

    # Get multi-line input from user
    print(f"{COLOR_BOLD}Enter the AI-generated text to humanize:{COLOR_END}")
    print(f"{COLOR_BLUE}(Press Enter, then Ctrl+D on Unix or Ctrl+Z on Windows + Enter to finish, or type 'exit' to quit){COLOR_END}\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().lower() == "exit" and not lines:
                print(f"\n{COLOR_WARNING}Exited application.{COLOR_END}")
                return
            lines.append(line)
        except EOFError:
            break

    input_text = "\n".join(lines)
    if not input_text.strip():
        print(f"\n{COLOR_FAIL}⚠ Input is empty. Please try again with some text.{COLOR_END}")
        return

    # Strength selection
    print(f"\n{COLOR_BOLD}Select Humanization Strength:{COLOR_END}")
    print(" [1] Low (Minimal changes, maintains structure)")
    print(" [2] Medium (Balanced phrasing & vocabulary adjustments) - Default")
    print(" [3] High (Highly conversational flow, splits sentences, additions)")
    
    strength_choice = input(f"\nChoose option [1-3] or press Enter for default: ").strip()
    strength = "Medium"
    if strength_choice == "1":
        strength = "Low"
    elif strength_choice == "3":
        strength = "High"

    # OpenAI API extension hook
    method = "local"
    api_key = None
    print(f"\n{COLOR_BOLD}Select Humanization Method:{COLOR_END}")
    print(" [1] Local rule-based engine (Fast, offline) - Default")
    print(" [2] OpenAI GPT Engine (Requires API Key)")
    
    method_choice = input(f"\nChoose option [1-2] or press Enter for default: ").strip()
    if method_choice == "2":
        method = "openai"
        api_key = input("Enter your OpenAI API Key (starts with sk-): ").strip()
        if not api_key:
            print(f"{COLOR_WARNING}⚠ No API key entered. Falling back to local engine.{COLOR_END}")
            method = "local"

    print(f"\n⌛ Humanizing text using {COLOR_BOLD}{method.upper()}{COLOR_END} engine (Strength: {COLOR_BOLD}{strength}{COLOR_END})...")
    
    try:
        humanized_text = humanize_text(input_text, strength=strength, method=method, openai_api_key=api_key)
        display_comparison(input_text, humanized_text)

        # Export choice
        export_choice = input(f"\nDo you want to export the humanized text to a .txt file? (y/N): ").strip().lower()
        if export_choice == "y":
            filepath = input("Enter output file path (e.g. output.txt): ").strip()
            if not filepath:
                filepath = "humanized_text.txt"
            save_to_file(humanized_text, filepath)

    except Exception as e:
        print(f"\n{COLOR_FAIL}✗ Error during humanization: {e}{COLOR_END}")
        
    print(f"\n{COLOR_GREEN}Thank you for using AI Text Humanizer!{COLOR_END}\n")


def main():
    """Main entrypoint for argparse/script invocation."""
    parser = argparse.ArgumentParser(
        description="Convert rigid AI-generated text to human-like text."
    )
    parser.add_argument("-i", "--input", help="Path to input text file.")
    parser.add_argument("-o", "--output", help="Path to save humanized output text file.")
    parser.add_argument("-s", "--strength", choices=["Low", "Medium", "High"], default="Medium",
                        help="Humanization strength. Default is Medium.")
    parser.add_argument("-m", "--method", choices=["local", "openai"], default="local",
                        help="Processing method. Default is local.")
    parser.add_argument("-k", "--key", help="OpenAI API Key (if method is openai).")
    
    # If no arguments are provided, launch the interactive loop
    if len(sys.argv) == 1:
        run_interactive()
        return

    args = parser.parse_args()

    # Read input
    if args.input:
        if not os.path.exists(args.input):
            print(f"{COLOR_FAIL}Error: Input file '{args.input}' not found.{COLOR_END}")
            sys.exit(1)
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        # Read from stdin
        print(f"Reading from standard input... (Press Ctrl+D or Ctrl+Z to finish)")
        text = sys.stdin.read()

    if not text.strip():
        print(f"{COLOR_WARNING}Input is empty. Nothing to humanize.{COLOR_END}")
        sys.exit(0)

    # Humanize
    try:
        humanized = humanize_text(
            text,
            strength=args.strength,
            method=args.method,
            openai_api_key=args.key or os.getenv("OPENAI_API_KEY")
        )
        
        # Output result
        if args.output:
            save_to_file(humanized, args.output)
        else:
            display_comparison(text, humanized)
    except Exception as e:
        print(f"{COLOR_FAIL}Error: {e}{COLOR_END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
