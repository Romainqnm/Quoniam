<p align="center">
  <img src="Intro.png" alt="Quoniam Banner" width="100%"/>
</p>

<h1 align="center">QUONIAM &mdash; Fluid Dynamics Audio Engine</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/GUI-Flet-02569B?logo=flutter&logoColor=white" alt="Flet"/>
  <img src="https://img.shields.io/badge/Audio-SCAMP%20%2B%20FluidSynth-FF6F00" alt="SCAMP"/>
  <img src="https://img.shields.io/badge/version-1.20-00E5FF" alt="v1.20"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License"/>
</p>

<p align="center">
  <b>A procedural audio environment for focus, relaxation, and flow.</b><br/>
  <i>Built with Python, Flet & SCAMP.</i>
</p>

---

## What is Quoniam?

Quoniam is a **generative audio engine** that creates infinite, non-repetitive soundscapes in real-time. Unlike a simple playlist, it uses Algorithmic Composition to generate unique melodies and harmonies on the fly, adapting to your mood and energy level.

---

## Key Features

### AI Conductor Engine (v1.20 — Organic Soul & Phrasing)
The **AI Conductor** replaces the random Auto-Drift system with an intelligent virtual conductor:
*   **Phrasing State**: Solo instruments enter long, legato phrases (15-40s) with natural note overlapping.
*   **Smart Envelopes**: Physically accurate sound shaping per instrument family:
    *   **SUSTAINED** (Strings, Winds, Organ): Gentle swell attack, dynamic sustain with breathing, long release tail (1-2.5s).
    *   **PERCUSSIVE** (Piano, Xylophone, Glockenspiel): Instant attack, natural exponential decay.
    *   **PLUCKED** (Pizzicato, Harp, Guitar, Harpsichord): Instant attack, short resonant decay (0.3-1.5s).
*   **Perlin Noise State Machine**: Tension, density, and valence evolve via smooth 1D noise curves.
*   **Instrument Tessitura**: Each instrument plays within its realistic MIDI range (e.g., Cello C2-A5, Flute C4-C7).
*   **Voice Leading**: Melodic instruments favor stepwise motion; disjoint leaps only during climaxes.
*   **Gaussian Humanization**: Velocity follows a natural bell curve.
*   **Scale Quantization**: All notes are snapped to the current scale with multi-octave awareness.

### Orchestra Mode (40+ Instruments)
Compose your own ensemble in real-time:
*   **Strings**: Violin, Viola, Cello, Contrabass, Guitar, Bass, Harp, Pizzicato
*   **Winds & Brass**: Flute, Piccolo, Clarinet, Oboe, Bassoon, French Horn, Trumpet, Brass Section
*   **Keys**: Grand Piano, Church Organ, Harpsichord, Accordion
*   **Percussion**: Timpani, Xylophone, Glockenspiel, Drums
*   **Ethereal**: Choir Aahs, Voice Oohs, Celesta, Tubular Bells

### Emotional Intelligence
The engine adapts based on 6 core emotions:
*   **Joy** / **Melancholy** / **Epic** / **Suspense** / **Action** / **Creative**

### Kaleidoscope Visualizer & Particle System (v1.20)
*   **Kaleidoscope**: 6+ radial shape types (petals, teardrops, diamonds, crescents, arcs), palette-synced with the current theme.
*   **Particle System**: 4 shape types (circles, diamonds, stars, dots) floating with BPM-synced pulsation and sinusoidal drift.
*   **Quality Settings**: Low / Medium / High — controls layer count, shape complexity, particle density, and glow effects.

### Settings, Recording & i18n (v1.20)
*   **Premium Settings Modal**: 900x600 glassmorphism overlay with gradient section cards (Visuals, App, Data).
*   **Fullscreen / FPS / Visual Quality**: Persistent controls read by both animation loops every frame.
*   **4 Languages**: English, French, Spanish, Arabic — hot-swappable from settings with full UI rebuild.
*   **Audio Recording**: Captures SCAMP performance to MIDI file with live timer.
*   **Persistence**: All settings survive app restarts via `page.client_storage`.

### Liquid Glass UI
*   **Glassmorphism**: Semi-transparent panels, blur effects, gradient borders.
*   **Compact Presets**: Pill-style preset buttons with radial glow icons.
*   **Focus Mode**: Hide all UI, only the kaleidoscope + particles remain. Exit via floating hint.
*   **Profiles**: Save and load your favorite instrument combinations.

---

## System Requirements

### FluidSynth (required by SCAMP)

SCAMP uses FluidSynth as its MIDI synthesizer backend. It must be installed **before** running Quoniam.

| Platform | Command |
|----------|---------|
| **Linux (Debian/Ubuntu)** | `sudo apt install fluidsynth` |
| **macOS (Homebrew)** | `brew install fluidsynth` |
| **Windows** | Generally bundled with the SCAMP pip wheel. If audio fails, install FluidSynth manually from [github.com/FluidSynth/fluidsynth/releases](https://github.com/FluidSynth/fluidsynth/releases). |

### SoundFont (required)

The audio engine needs a **General MIDI SoundFont** (`.sf2`) to produce sound. The recommended file is **FluidR3_GM.sf2**.

1.  Download `FluidR3_GM.sf2` from [MuseScore's SoundFont repository](https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/) or search for "FluidR3_GM.sf2" on any trusted SoundFont archive.
2.  Place the file in the **project root folder** (`Quoniam/FluidR3_GM.sf2`).

> Without this file, the Orchestra / SCAMP engine will not produce any audio output.

---

## Installation & Run

```bash
# Clone the repository
git clone https://github.com/Romainqnm/Quoniam.git
cd Quoniam

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python interface.py
```

**Dependencies** (installed via pip):
| Package | Purpose |
|---------|---------|
| `flet>=0.10.0` | GUI framework (Flutter for Python) |
| `scamp>=0.9.0` | MIDI audio generation engine |
| `pygame>=2.5.0` | Ambient loop audio playback |

---

## Missing Audio Files

The loop-based ambient modes (**Elements**, **Seasons**, **Atmos**) require audio sample files that are **not included** in this repository due to file size and licensing.

To enable these modes, add your own audio files to the `assets/sounds/` directory, matching the filenames below:

```
assets/sounds/
├── rain.flac           # Elements: Water
├── fire.wav            # Elements: Fire
├── forest.wav          # Elements: Earth
├── wind.flac           # Elements: Air
├── drone_space.wav     # Elements: Space
├── winter_wind.wav     # Seasons: Winter
├── birds.wav           # Seasons: Spring
├── crickets.wav        # Seasons: Summer
├── rain_leaves.wav     # Seasons: Autumn
├── white_noise.aiff    # Seasons: Void
├── bowl.wav            # Atmos: Zen
├── glitchwav.wav       # Atmos: Cyber
├── vinyl.mp3           # Atmos: LoFi
├── thunder.wav         # Atmos: Thunder
└── traffic.wav         # Atmos: Traffic
```

Any `.wav`, `.mp3`, `.flac`, or `.aiff` file will work. Choose ambient loops that match the theme names for the best experience.

> A future update will bundle royalty-free default samples so these modes work out of the box.

---

## Project Structure (v1.20)

```
Quoniam/
├── ai_conductor.py      # AI Conductor (Perlin noise, phrasing, smart envelopes)
├── audio_engine.py      # SCAMP audio engine (class-based, recording, robust loading)
├── interface.py         # Flet UI (Liquid Glass, kaleidoscope, particles, settings, i18n)
├── config.py            # Global state, settings persistence, translations (4 languages)
├── gammes.py            # Musical scales database
├── assets_library.py    # SVG icons & visual assets
├── main.py              # Standalone engine runner
├── requirements.txt     # Python dependencies
├── Intro.png            # Banner image
├── assets/sounds/       # Ambient audio loops (user-provided, see above)
├── recordings/          # MIDI recording output (auto-created)
└── FluidR3_GM.sf2       # SoundFont (not included, download separately)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Core** | Python 3.11+ |
| **GUI** | [Flet](https://flet.dev) (Flutter for Python) |
| **Audio Generation** | [SCAMP](http://scamp.marcevanstein.com/) + FluidSynth |
| **Ambient Playback** | Pygame mixer (dual-channel crossfade) |
| **AI Conductor** | Custom `AIConductor` class (Perlin noise, voice leading, tessitura) |
| **Synth** | `FluidR3_GM.sf2` (General MIDI SoundFont) |
| **i18n** | 129 translation keys x 4 languages (EN, FR, ES, AR) |
