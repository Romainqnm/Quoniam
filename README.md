# 🌊 QUONIAM: Fluid Dynamics Audio Engine (v15.0)

> **A procedural audio environment for focus, relaxation, and flow.**
> *Built with Python, Flet & SCAMP.*

![Quoniam Banner](Intro.png)

## 🔮 What is Quoniam?
Quoniam | Audio is a **generative audio engine** that creates infinite, non-repetitive soundscapes in real-time. Unlike a simple playlist, it uses Algorithmic Composition to generate unique melodies and harmonies on the fly, adapting to your mood and energy level.

## ✨ Key Features (v15.0 - "Nappes Fluides")

### 🎵 NEW: Fluid Sound Layers
**v15.0 introduces continuous, overlapping sound tapestries:**
*   **Dynamic Envelopes**: Notes now feature organic fade-in/fade-out curves (no more abrupt cuts!)
*   **Parallel Processing**: Multiple notes play simultaneously using SCAMP's `fork()` system
*   **Temporal Overlap**: 50% note overlap creates seamless, flowing soundscapes
*   **Extended Sustain**: Notes ring for 3-6 seconds with natural decay

**Result**: Smooth, atmospheric sound like a real orchestra, not a MIDI sequencer.

### 🏗️ NEW: Refactored Architecture
**Clean separation of concerns:**
*   **`audio_engine.py`**: Dedicated `QuoniamAudioEngine` class (threading, SCAMP logic)
*   **`interface.py`**: Pure UI layer (Flet components only)
*   **Easy Integration**: Simple API (`start()`, `stop()`, `set_volume()`, `set_mood()`)

See [`CHANGELOG_v15.md`](CHANGELOG_v15.md) for migration details.

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

### 🎛️ Audio Engine v15.0 (Nappes Fluides)
A state-of-the-art procedural engine designed for organic realism:
*   **Fluid Envelopes**: Dynamic fade-in/fade-out curves for smooth, continuous sound
*   **Smart Polyphony**: Distinguishes between chord instruments (Piano, Harp) and melodic instruments (Violin, Flute) to prevent muddy mixes
*   **Temporal Overlap**: 50% note overlapping creates seamless layers instead of gaps
*   **Infinite Sustain**: Atmospheric note decays (up to 8s) for deep immersion
*   **Wandering Tempo**: The BPM micro-drifts (+/- 15 BPM) over time to simulate a live human performance

### 🌊 Auto-Drift & Zen Mode
Turn on **Auto Mode** and let the engine take control.
*   **Zen Intro**: A soft, progressive 30-second start to ease you into the flow.
*   **Evolving Soundscape**: Instruments are added and removed automatically based on the emotional trajectory.
*   **Parameter Drift**: Intensity and speed fluctuate naturally over time.

### 🎨 Visual & UI
*   **Liquid Glass UI**: A modern interface with neon dividers, glassmorphism, and responsive layouts.
*   **Audio-Reactive Visualizer**: A particle system (Orbs, Petals, Bubbles) that pulsates with the music's intensity and theme.
*   **Profiles**: Save and load your favorite instrument combinations and settings.

## 🛠️ Tech Stack
*   **Core**: Python 3.11+
*   **GUI**: [Flet](https://flet.dev) (Flutter for Python)
*   **Audio Generation**: [SCAMP](http://scamp.marcevanstein.com/) & FluidSynth
*   **Audio Engine**: Custom `QuoniamAudioEngine` class (v15.0)
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

## 📦 Project Structure (v15.0)
```
Quoniam/
├── audio_engine.py      # 🆕 SCAMP audio engine (class-based)
├── interface.py         # Flet UI (refactored, cleaner)
├── config.py            # Global state & settings
├── gammes.py            # Musical scales database
├── assets_library.py    # SVG icons & visual assets
├── main.py              # Legacy entry point (deprecated)
├── requirements.txt     # 🆕 Dependencies
├── CHANGELOG_v15.md     # 🆕 Migration guide
└── FluidR3_GM.sf2       # SoundFont (not included, download separately)
```
