"""Music theory primitives: notes, intervals, modes, scales, and chord construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence


NOTE_TO_SEMITONE: Dict[str, int] = {
    "C": 0,
    "C#": 1,
    "DB": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "GB": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "B": 11,
}
SEMITONE_TO_NOTE = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}

MODES: Dict[str, List[int]] = {
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
}

INTERVALS: Dict[str, int] = {
    "P1": 0,
    "m2": 1,
    "M2": 2,
    "m3": 3,
    "M3": 4,
    "P4": 5,
    "TT": 6,
    "P5": 7,
    "m6": 8,
    "M6": 9,
    "m7": 10,
    "M7": 11,
    "P8": 12,
    "M9": 14,
    "P11": 17,
    "M13": 21,
}


@dataclass(frozen=True)
class Scale:
    root: str
    mode: str

    def pitch_classes(self) -> List[int]:
        root_pc = NOTE_TO_SEMITONE[self.normalized_root()]
        return [(root_pc + interval) % 12 for interval in MODES[self.mode]]

    def normalized_root(self) -> str:
        return normalize_note_name(self.root)

    def degree_to_pitch_class(self, degree: int) -> int:
        scale = self.pitch_classes()
        return scale[(degree - 1) % 7]

    def degree_to_note_name(self, degree: int) -> str:
        return SEMITONE_TO_NOTE[self.degree_to_pitch_class(degree)]


@dataclass(frozen=True)
class Chord:
    root: str
    quality: str
    pitch_classes: Sequence[int]
    function: str
    symbol: str


def normalize_note_name(note: str) -> str:
    note = note.strip().upper().replace("♭", "B").replace("♯", "#")
    if note not in NOTE_TO_SEMITONE:
        raise ValueError(f"Unknown note name: {note}")
    return note


def build_scale(root: str, mode: str) -> Scale:
    mode = mode.lower()
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    return Scale(root=root, mode=mode)


def build_chord_from_scale(
    scale: Scale, degree: int, extensions: Sequence[int] | None = None
) -> Chord:
    """Build a 7th/extended chord from a scale degree.

    Extensions are scale degrees above the 7th (9, 11, 13). They add color tones.
    """
    if extensions is None:
        extensions = []
    chord_degrees = [degree, degree + 2, degree + 4, degree + 6]
    chord_degrees.extend(extensions)
    pitch_classes = [scale.degree_to_pitch_class(d) for d in chord_degrees]
    root_pc = pitch_classes[0]
    quality = detect_quality(pitch_classes)
    symbol = f"{SEMITONE_TO_NOTE[root_pc]}{quality}"
    return Chord(
        root=SEMITONE_TO_NOTE[root_pc],
        quality=quality,
        pitch_classes=pitch_classes,
        function=function_from_degree(degree, scale.mode),
        symbol=symbol,
    )


def detect_quality(pitch_classes: Sequence[int]) -> str:
    """Determine chord quality by intervals above the root."""
    if not pitch_classes:
        return ""
    root = pitch_classes[0]
    intervals = sorted(((pc - root) % 12 for pc in pitch_classes[1:]))
    triad = intervals[:2]
    seventh = 10 if 10 in intervals else 11 if 11 in intervals else None
    if triad == [3, 7]:
        quality = "m"
    elif triad == [4, 7]:
        quality = ""
    elif triad == [3, 6]:
        quality = "dim"
    else:
        quality = "sus"
    if seventh == 10:
        quality += "7"
    elif seventh == 11:
        quality += "maj7"
    return quality


def function_from_degree(degree: int, mode: str) -> str:
    if mode in {"ionian", "lydian", "mixolydian"}:
        if degree in {1, 3, 6}:
            return "tonic"
        if degree in {2, 4}:
            return "predominant"
        return "dominant"
    if degree in {1, 3, 6}:
        return "tonic"
    if degree in {2, 4}:
        return "predominant"
    return "dominant"


def midi_pitch(note: str, octave: int) -> int:
    pc = NOTE_TO_SEMITONE[normalize_note_name(note)]
    return 12 * (octave + 1) + pc
