# 🌊 QUONIAM: Fluid Dynamics Audio Engine (v18.0)

> **A procedural audio environment for focus, relaxation, and flow.**
> *Built with Python, Flet & SCAMP.*

![Quoniam Banner](Intro.png)

## 🔮 What is Quoniam?
Quoniam | Audio is a **generative audio engine** that creates infinite, non-repetitive soundscapes in real-time. Unlike a simple playlist, it uses Algorithmic Composition to generate unique melodies and harmonies on the fly, adapting to your mood and energy level.

## ✨ Key Features

### 🧠 AI Conductor Engine (v18.0)
The **AI Conductor** replaces the random Auto-Drift system with an intelligent virtual conductor:
*   **Perlin Noise State Machine**: Tension, density, and valence evolve via smooth 1D noise curves instead of random jumps — music "undulates" organically instead of flickering chaotically.
*   **Instrument Tessitura**: Each instrument is constrained to its realistic MIDI range (e.g., Cello C2–A5, Flute C4–C7). No more mosquito-pitched cellos or inaudible bass flutes.
*   **Voice Leading**: Melodic instruments favor stepwise motion (conjoint degrees); disjoint leaps only occur during high-tension climaxes.
*   **Gaussian Humanization**: Velocity follows a natural bell curve (`random.gauss`) instead of uniform randomness — notes feel played by a human, not a robot.
*   **Scale Quantization**: All generated notes are snapped to the current scale (Dorian, Harmonic Minor, Pentatonic, etc.) with multi-octave awareness.
*   **Spectral Awareness**: Prevents frequency masking (e.g., bass and sub-bass won't play simultaneously).
*   **Dynamic Orchestration**: Low tension → sparse textures (few instruments, long sustained notes). High tension → dense tutti (full orchestra, rapid rhythmic patterns).

### 🎵 Fluid Sound Layers
*   **Dynamic Envelopes**: Notes feature organic fade-in/fade-out curves (no more abrupt cuts!)
*   **Parallel Processing**: Multiple notes play simultaneously using SCAMP's `fork()` system
*   **Temporal Overlap**: 50% note overlap creates seamless, flowing soundscapes
*   **Extended Sustain**: Notes ring for 3-6 seconds with natural decay

### 🏗️ Refactored Architecture
**Clean separation of concerns:**
*   **`audio_engine.py`**: Dedicated `QuoniamAudioEngine` class (threading, SCAMP logic)
*   **`ai_conductor.py`**: `AIConductor` class (Perlin noise, voice leading, tessitura, orchestration)
*   **`interface.py`**: Pure UI layer (Flet components only)
*   **Easy Integration**: Simple API (`start()`, `stop()`, `set_volume()`, `set_mood()`)

### 🎻 Orchestra Mode
Compose your own ensemble in real-time! Select from over 30 high-quality instruments including:
*   **Strings**: Violin, Cello, Contrabass, Pizzicato, Harp.
*   **Winds**: Flute, Oboe, Clarinet, French Horn, Saxophone.
*   **Keys**: Grand Piano, Church Organ, Celesta, Marimba.
*   **Ethereal**: Choir, Voice Oohs, Halo Pad, Crystal.

### 🧠 Emotional Intelligence
The engine adapts its playing style based on 6 core emotions:
*   **Joy**: Major scales, bright instruments, upbeat tempo.
*   **Melancolique**: Minor scales, slow strings, deep cello.
*   **Epic**: Powerful brass, percussion, grand orchestration.
*   **Suspense**: Dissonant harmonies, low piano rumbles, uneasy silence.
*   **Action**: Fast rhythms, staccato strings, driving drums.
*   **Creative**: No rules, pure random exploration.

### 🎛️ Audio Engine
A state-of-the-art procedural engine designed for organic realism:
*   **Fluid Envelopes**: Dynamic fade-in/fade-out curves for smooth, continuous sound
*   **Smart Polyphony**: Distinguishes between chord instruments (Piano, Harp) and melodic instruments (Violin, Flute) to prevent muddy mixes
*   **Temporal Overlap**: 50% note overlapping creates seamless layers instead of gaps
*   **Infinite Sustain**: Atmospheric note decays (up to 8s) for deep immersion
*   **Wandering Tempo**: The BPM micro-drifts smoothly via Perlin noise to simulate a live human performance

### 🌊 Auto-Drift & Zen Mode
Turn on **Auto Mode** and let the AI Conductor take control.
*   **Zen Intro**: A soft, progressive 30-second start to ease you into the flow.
*   **Evolving Soundscape**: Instruments are added and removed intelligently based on density and spectral balance.
*   **Parameter Drift**: Tension, intensity, and tempo evolve organically via Perlin noise curves.

### 🎨 Visual & UI
*   **Liquid Glass UI**: A modern interface with glassmorphism, compact pill-style presets, and responsive layouts.
*   **Dual Visualizer**: Kaleidoscope canvas in focus mode, soft particle system on home screen.
*   **Profiles**: Save and load your favorite instrument combinations and settings.

## 🛠️ Tech Stack
*   **Core**: Python 3.11+
*   **GUI**: [Flet](https://flet.dev) (Flutter for Python)
*   **Audio Generation**: [SCAMP](http://scamp.marcevanstein.com/) & FluidSynth
*   **AI Conductor**: Custom `AIConductor` class (Perlin noise, voice leading, tessitura)
*   **Synth**: `FluidR3_GM.sf2` (General MIDI SoundFont)

## 🚀 Installation & Run
```bash
# Clone the repository
git clone https://github.com/Romainqnm/Quoniam.git
cd Quoniam

# Install dependencies
pip install -r requirements.txt

# Run the engine
python interface.py
```

## 📦 Project Structure (v18.0)
```
Quoniam/
├── ai_conductor.py      # 🆕 AI Conductor (Perlin noise, voice leading, tessitura)
├── audio_engine.py      # SCAMP audio engine (class-based)
├── interface.py         # Flet UI (Liquid Glass, dual visualizer)
├── config.py            # Global state & settings
├── gammes.py            # Musical scales database
├── assets_library.py    # SVG icons & visual assets
├── main.py              # Legacy entry point (deprecated)
├── requirements.txt     # Dependencies
├── CHANGELOG_v15.md     # Migration guide
└── FluidR3_GM.sf2       # SoundFont (not included, download separately)
```
