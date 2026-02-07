"""CLI entry point for generating MIDI compositions."""

from __future__ import annotations

import argparse

from .composition import Composer
from .midi import MidiRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate theory-driven music as MIDI.")
    parser.add_argument("--root", default="C", help="Root note for the main key.")
    parser.add_argument(
        "--mode",
        default="ionian",
        help="Mode to use (ionian, dorian, etc.) or 'auto' to use style default.",
    )
    parser.add_argument(
        "--style",
        default="classical",
        choices=["classical", "jazz", "pop", "cinematic"],
        help="Style preset controlling tempo and rhythm.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument("--output", default="output.mid", help="Output MIDI filename.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    composer = Composer(root=args.root, mode=args.mode, style=args.style, seed=args.seed)
    composition = composer.compose()
    renderer = MidiRenderer()
    renderer.render(composition, args.output)
    print(f"Generated MIDI saved to {args.output}")


if __name__ == "__main__":
    main()
