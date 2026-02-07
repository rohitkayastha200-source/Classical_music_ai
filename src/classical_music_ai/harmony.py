"""Harmonic planning utilities: functional harmony, secondary dominants, modulations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .theory import SEMITONE_TO_NOTE, Chord, Scale, build_chord_from_scale, build_scale


RELATED_KEY_OFFSETS = {
    "relative": 9,  # relative minor/major (down a minor third / up a major sixth)
    "dominant": 7,
    "subdominant": 5,
}


@dataclass
class HarmonicContext:
    scale: Scale
    mode: str
    tonic_degree: int = 1


def choose_related_key(root: str, mode: str, relation: str) -> Scale:
    scale = build_scale(root, mode)
    offset = RELATED_KEY_OFFSETS[relation]
    new_root_pc = (scale.pitch_classes()[0] + offset) % 12
    new_root = SEMITONE_TO_NOTE[new_root_pc]
    return build_scale(new_root, mode)


def functional_progression(scale: Scale, length: int) -> List[int]:
    """Return a sequence of scale degrees that obey tonic-predominant-dominant logic."""
    progression = [1]
    while len(progression) < length:
        if len(progression) % 4 == 3:
            progression.append(5)
        elif len(progression) % 4 == 0:
            progression.append(1)
        else:
            if progression[-1] in {1, 6}:
                progression.append(4)
            elif progression[-1] in {2, 4}:
                progression.append(5)
            else:
                progression.append(1)
    return progression[:length]


def add_secondary_dominants(degrees: Sequence[int]) -> List[int]:
    """Insert secondary dominants by preceding predominant/dominant chords."""
    decorated: List[int] = []
    for degree in degrees:
        if degree in {2, 5}:
            decorated.append((degree + 4) % 7 or 7)
        decorated.append(degree)
    return decorated


def build_chord_progression(scale: Scale, length: int, use_secondary: bool = True) -> List[Chord]:
    degrees = functional_progression(scale, length)
    if use_secondary:
        degrees = add_secondary_dominants(degrees)
    chords = []
    for degree in degrees:
        extensions = [9] if degree in {2, 4} else [9, 11] if degree == 5 else []
        chords.append(build_chord_from_scale(scale, degree, extensions=extensions))
    return chords


def apply_modulation(scale: Scale, relation: str) -> Scale:
    relation = relation.lower()
    if relation not in RELATED_KEY_OFFSETS:
        raise ValueError(f"Unknown relation: {relation}")
    return choose_related_key(scale.root, scale.mode, relation)
