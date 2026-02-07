"""Composition engine that applies theory-driven rules to build music."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from .harmony import apply_modulation, build_chord_progression
from .rhythm import RhythmPattern, build_rhythm_pattern
from .theory import Chord, Scale, build_scale, midi_pitch


@dataclass
class Section:
    name: str
    chords: List[Chord]
    melody: List[Tuple[int, float, float, int]]
    bass: List[Tuple[int, float, float, int]]


STYLE_PRESETS: Dict[str, Dict[str, object]] = {
    "classical": {
        "tempo": 96,
        "mode": "ionian",
        "swing": 0.0,
        "rhythms": ["straight", "lilting"],
        "register": (60, 84),
    },
    "jazz": {
        "tempo": 120,
        "mode": "dorian",
        "swing": 0.18,
        "rhythms": ["swing", "syncopated"],
        "register": (60, 88),
    },
    "pop": {
        "tempo": 110,
        "mode": "ionian",
        "swing": 0.08,
        "rhythms": ["syncopated", "straight"],
        "register": (64, 84),
    },
    "cinematic": {
        "tempo": 80,
        "mode": "aeolian",
        "swing": 0.0,
        "rhythms": ["lilting", "straight"],
        "register": (55, 80),
    },
}


class Composer:
    def __init__(
        self,
        root: str = "C",
        mode: str = "ionian",
        style: str = "classical",
        seed: int | None = None,
    ) -> None:
        self.style = STYLE_PRESETS.get(style, STYLE_PRESETS["classical"])
        self.root = root
        self.mode = self.style["mode"] if mode == "auto" else mode
        if seed is not None:
            random.seed(seed)

    def compose(self) -> Dict[str, object]:
        scale = build_scale(self.root, self.mode)
        sections = [
            self._build_section("verse", scale, 8),
            self._build_section("chorus", scale, 8),
        ]
        modulated_scale = apply_modulation(scale, random.choice(["dominant", "relative"]))
        sections.append(self._build_section("bridge", modulated_scale, 6))
        sections.append(self._build_section("chorus", scale, 8))
        return {
            "tempo": self.style["tempo"],
            "swing": self.style["swing"],
            "sections": sections,
        }

    def _build_section(self, name: str, scale: Scale, bars: int) -> Section:
        chord_progression = build_chord_progression(scale, bars)
        rhythm_name = random.choice(self.style["rhythms"])
        rhythm_pattern = build_rhythm_pattern(rhythm_name)
        melody = self._generate_melody(chord_progression, rhythm_pattern)
        bass = self._generate_bass(chord_progression)
        return Section(name=name, chords=chord_progression, melody=melody, bass=bass)

    def _generate_melody(
        self, chords: Sequence[Chord], rhythm: RhythmPattern
    ) -> List[Tuple[int, float, float, int]]:
        register_low, register_high = self.style["register"]
        motif = [0, 2, -1, 3, -2, 1]
        melody: List[Tuple[int, float, float, int]] = []
        current_pitch = random.randint(register_low, register_high)
        time = 0.0
        for idx, chord in enumerate(chords):
            for dur in rhythm.pattern:
                # Favor chord tones for stability; occasional color tones for motion.
                if random.random() < 0.7:
                    target_pc = chord.pitch_classes[idx % len(chord.pitch_classes)]
                else:
                    target_pc = chord.pitch_classes[(idx + 2) % len(chord.pitch_classes)]
                candidate = self._closest_pitch(target_pc, current_pitch, register_low, register_high)
                # Motif-driven contour supports thematic repetition.
                if random.random() < 0.35:
                    candidate += motif[idx % len(motif)]
                velocity = self._human_velocity(76, 15)
                melody.append((candidate, time, dur, velocity))
                current_pitch = candidate
                time += dur
        return melody

    def _generate_bass(self, chords: Sequence[Chord]) -> List[Tuple[int, float, float, int]]:
        bass: List[Tuple[int, float, float, int]] = []
        time = 0.0
        for chord in chords:
            root_pc = chord.pitch_classes[0]
            root_note = self._closest_pitch(root_pc, 36, 32, 48)
            bass.append((root_note, time, 1.0, self._human_velocity(80, 8)))
            bass.append((root_note + 12, time + 2.0, 0.5, self._human_velocity(70, 10)))
            time += 4.0
        return bass

    def _closest_pitch(self, target_pc: int, anchor: int, low: int, high: int) -> int:
        candidates = [p for p in range(low, high + 1) if p % 12 == target_pc]
        return min(candidates, key=lambda p: abs(p - anchor))

    def _human_velocity(self, base: int, variation: int) -> int:
        return max(40, min(120, int(random.gauss(base, variation))))
