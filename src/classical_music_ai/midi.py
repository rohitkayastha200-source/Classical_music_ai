"""MIDI rendering utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import mido

from .composition import Section


@dataclass
class MidiTrackData:
    name: str
    channel: int
    program: int
    notes: List[Tuple[int, float, float, int]]


class MidiRenderer:
    def __init__(self, ticks_per_beat: int = 480) -> None:
        self.ticks_per_beat = ticks_per_beat

    def render(self, composition: Dict[str, object], output_path: str) -> None:
        midi = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        tempo = mido.bpm2tempo(int(composition["tempo"]))
        swing = float(composition["swing"])

        melody_notes: List[Tuple[int, float, float, int]] = []
        harmony_notes: List[Tuple[int, float, float, int]] = []
        bass_notes: List[Tuple[int, float, float, int]] = []
        drum_notes: List[Tuple[int, float, float, int]] = []
        time_offset = 0.0

        for section in composition["sections"]:
            section = section  # type: Section
            melody_notes.extend(self._offset_notes(section.melody, time_offset, swing))
            harmony_notes.extend(self._chord_notes(section.chords, time_offset))
            bass_notes.extend(self._offset_notes(section.bass, time_offset, 0.0))
            drum_notes.extend(self._drum_pattern(len(section.chords), time_offset))
            time_offset += len(section.chords) * 4.0

        tracks = [
            MidiTrackData("Melody", 0, 40, melody_notes),
            MidiTrackData("Harmony", 1, 48, harmony_notes),
            MidiTrackData("Bass", 2, 32, bass_notes),
            MidiTrackData("Drums", 9, 0, drum_notes),
        ]

        tempo_track = mido.MidiTrack()
        tempo_track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
        midi.tracks.append(tempo_track)

        for track_data in tracks:
            track = mido.MidiTrack()
            track.append(mido.MetaMessage("track_name", name=track_data.name, time=0))
            if track_data.channel != 9:
                track.append(
                    mido.Message(
                        "program_change",
                        channel=track_data.channel,
                        program=track_data.program,
                        time=0,
                    )
                )
            self._write_notes(track, track_data.notes, track_data.channel)
            midi.tracks.append(track)

        midi.save(output_path)

    def _write_notes(
        self,
        track: mido.MidiTrack,
        notes: Sequence[Tuple[int, float, float, int]],
        channel: int,
    ) -> None:
        events = []
        for pitch, start, duration, velocity in notes:
            events.append((start, True, pitch, velocity))
            events.append((start + duration, False, pitch, 0))
        events.sort(key=lambda x: x[0])
        current_time = 0.0
        for event_time, is_on, pitch, velocity in events:
            delta = event_time - current_time
            current_time = event_time
            ticks = int(delta * self.ticks_per_beat)
            message_type = "note_on" if is_on else "note_off"
            track.append(
                mido.Message(
                    message_type,
                    note=pitch,
                    velocity=velocity,
                    time=ticks,
                    channel=channel,
                )
            )

    def _offset_notes(
        self,
        notes: Sequence[Tuple[int, float, float, int]],
        offset: float,
        swing: float,
    ) -> List[Tuple[int, float, float, int]]:
        swung: List[Tuple[int, float, float, int]] = []
        for pitch, start, duration, velocity in notes:
            swing_offset = swing if int(start * 2) % 2 == 1 else 0.0
            swung.append((pitch, start + offset + swing_offset, duration, velocity))
        return swung

    def _chord_notes(self, chords, offset: float) -> List[Tuple[int, float, float, int]]:
        notes: List[Tuple[int, float, float, int]] = []
        time = offset
        previous_voicing: List[int] | None = None
        for chord in chords:
            chord_pitches = self._voice_lead_chord(chord.pitch_classes[:4], previous_voicing)
            previous_voicing = chord_pitches
            for pitch in chord_pitches:
                notes.append((pitch, time, 4.0, 60))
            time += 4.0
        return notes

    def _voice_lead_chord(
        self, pitch_classes: Sequence[int], previous_voicing: List[int] | None
    ) -> List[int]:
        base = 48
        chord = [base + pc for pc in pitch_classes]
        if previous_voicing is None:
            return chord
        candidates = []
        for inversion in range(len(chord)):
            voicing = chord[inversion:] + [p + 12 for p in chord[:inversion]]
            distance = sum(abs(a - b) for a, b in zip(previous_voicing, voicing))
            candidates.append((distance, voicing))
        return min(candidates, key=lambda x: x[0])[1]

    def _drum_pattern(self, bars: int, offset: float) -> List[Tuple[int, float, float, int]]:
        notes: List[Tuple[int, float, float, int]] = []
        time = offset
        for _ in range(bars):
            notes.append((36, time, 0.5, 96))
            notes.append((42, time + 0.5, 0.25, 70))
            notes.append((38, time + 1.0, 0.5, 90))
            notes.append((42, time + 1.5, 0.25, 68))
            notes.append((36, time + 2.0, 0.5, 92))
            notes.append((42, time + 2.5, 0.25, 70))
            notes.append((38, time + 3.0, 0.5, 88))
            notes.append((42, time + 3.5, 0.25, 65))
            time += 4.0
        return notes
