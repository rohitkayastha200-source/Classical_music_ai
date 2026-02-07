"""Rhythm generation with syncopation and expressive timing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RhythmPattern:
    name: str
    pattern: List[float]


RHYTHM_LIBRARY: Dict[str, RhythmPattern] = {
    "straight": RhythmPattern("straight", [1.0, 1.0, 1.0, 1.0]),
    "lilting": RhythmPattern("lilting", [1.5, 0.5, 1.0, 1.0]),
    "syncopated": RhythmPattern("syncopated", [0.75, 0.25, 1.5, 0.5, 1.0]),
    "swing": RhythmPattern("swing", [0.66, 0.34, 0.66, 0.34, 1.0, 1.0]),
}


def build_rhythm_pattern(name: str) -> RhythmPattern:
    return RHYTHM_LIBRARY.get(name, RHYTHM_LIBRARY["straight"])
