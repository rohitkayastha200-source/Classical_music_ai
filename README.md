# Classical Music AI

A theory-driven Python music generator that composes structured pieces with functional harmony, modulation, motifs, and expressive rhythm. The output is a playable MIDI file with separate melody, harmony, bass, and drums tracks.

## Features
- **Music theory engine**: notes, intervals, modes, scales, and extended chords.
- **Functional harmony**: tonic–predominant–dominant flow with secondary dominants.
- **Modulation**: shifts to related keys mid-song.
- **Motivic melody**: chord tones + passing tones with voice-leading.
- **Rhythm & expression**: syncopation, swing, and humanized velocity.
- **Orchestration**: multi-track MIDI (melody, harmony, bass, drums).
- **Style presets**: classical, jazz, pop, cinematic.

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python -m classical_music_ai.main --root C --mode ionian --style classical --output output.mid
```

### Style presets
- `classical`: balanced harmonic motion with straight rhythms.
- `jazz`: dorian mode, swing, richer extensions.
- `pop`: syncopated rhythms in major.
- `cinematic`: slower tempo with darker modal color.

## Project structure
```
src/classical_music_ai/
  composition.py   # Form + melody + bass
  harmony.py       # Functional harmony & modulations
  midi.py          # MIDI rendering
  rhythm.py        # Rhythm patterns
  theory.py        # Notes, modes, scales, chords
  main.py          # CLI entry point
```

## Extending
Add new styles by extending `STYLE_PRESETS` in `composition.py`, or introduce new rhythm patterns in `rhythm.py`.
