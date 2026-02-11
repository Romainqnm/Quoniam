# 🌊 QUONIAM: Fluid Dynamics Audio Engine (v1.19.2)

> **A procedural audio environment for focus, relaxation, and flow.**
> *Built with Python, Flet & SCAMP.*

![Quoniam Banner](Intro.png)

## 🔮 What is Quoniam?
Quoniam | Audio is a **generative audio engine** that creates infinite, non-repetitive soundscapes in real-time. Unlike a simple playlist, it uses Algorithmic Composition to generate unique melodies and harmonies on the fly, adapting to your mood and energy level.

## ✨ Key Features

### 🧠 AI Conductor Engine (v1.19.2 — Organic Soul & Phrasing)
The **AI Conductor** replaces the random Auto-Drift system with an intelligent virtual conductor:
*   **Phrasing State**: Solo instruments enter long, legato phrases (15-40s) with natural note overlapping — no more robotic, isolated notes.
*   **Smart Envelopes**: Physically accurate sound shaping per instrument family:
    *   **SUSTAINED** (Strings, Winds, Organ): Gentle swell attack → dynamic sustain with breathing → long release tail (1-2.5s).
    *   **PERCUSSIVE** (Piano, Xylophone, Glockenspiel): Instant attack → natural exponential decay.
    *   **PLUCKED** (Pizzicato, Harp, Guitar, Harpsichord): Instant attack → short resonant decay (0.3-1.5s).
*   **Continuum Mélodique**: Sustained instruments maintain a continuous sound with no silence between notes — natural crossfades (tuilage) are guaranteed.
*   **Perlin Noise State Machine**: Tension, density, and valence evolve via smooth 1D noise curves — music undulates organically.
*   **Instrument Tessitura**: Each instrument plays within its realistic MIDI range (e.g., Cello C2–A5, Flute C4–C7).
*   **Voice Leading**: Melodic instruments favor stepwise motion; disjoint leaps only during climaxes.
*   **Gaussian Humanization**: Velocity follows a natural bell curve — notes feel played by a human.
*   **Scale Quantization**: All notes are snapped to the current scale with multi-octave awareness.
*   **Spectral Awareness**: Prevents frequency masking (bass and sub-bass won't collide).

### 🎵 Fluid Sound Layers
*   **Dynamic Envelopes**: Organic fade-in/fade-out curves — no more abrupt cuts
*   **Parallel Processing**: Multiple notes play simultaneously using SCAMP's `fork()` system
*   **Legato Overlap**: 70-90% note overlap creates seamless, flowing soundscapes
*   **Pillar Notes**: Sustained instruments hold notes for 4-8 seconds with natural decay

### 🎻 Orchestra Mode (40+ Instruments)
Compose your own ensemble in real-time! Select from over **40 high-quality instruments**:
*   **Strings**: Violin, Viola, Cello, Contrabass, Guitar, Bass, Harp, Pizzicato
*   **Winds & Brass**: Flute, Piccolo, Clarinet, Oboe, Bassoon, French Horn, Trumpet, Brass Section
*   **Keys**: Grand Piano, Church Organ, Harpsichord, Accordion
*   **Percussion**: Timpani, Xylophone, Glockenspiel, Drums
*   **Ethereal**: Choir Aahs, Voice Oohs, Celesta, Tubular Bells

### 🧠 Emotional Intelligence
The engine adapts its playing style based on 6 core emotions:
*   **Joy**: Major scales, bright instruments, upbeat tempo
*   **Mélancolique**: Minor scales, slow strings, deep cello
*   **Épique**: Powerful brass, percussion, grand orchestration
*   **Suspense**: Dissonant harmonies, low piano rumbles, uneasy silence
*   **Action**: Fast rhythms, staccato strings, driving drums
*   **Créatif**: No rules, pure random exploration

### ✨ Particle System (NEW in v1.19.2)
Ambient particles float across the visualizer, synced with the music:
*   **4 Shape Types**: Circles, diamonds, 4-pointed stars, tiny sparkle dots
*   **Palette-Synced Colors**: Particles inherit the current kaleidoscope theme colors
*   **Organic Motion**: Slow upward drift with sinusoidal horizontal wobble
*   **BPM-Synced Pulsation**: Particle sizes breathe with the musical tempo
*   **Adaptive Density**: 15-27 particles on screen, scaling with audio intensity
*   **Lifecycle**: Smooth fade-in → float → fade-out (3-5.5s lifespan)

### 🎨 Visual & UI
*   **Liquid Glass UI**: Modern interface with glassmorphism, compact pill-style presets
*   **Kaleidoscope Visualizer**: 6+ shape types (petals, teardrops, diamonds, crescents, arcs)
*   **Dual Mode**: Kaleidoscope canvas in focus mode, ambient particles everywhere
*   **Profiles**: Save and load your favorite instrument combinations

### 🎛️ Audio Engine
*   **Fluid Envelopes**: Dynamic fade-in/fade-out curves for smooth, continuous sound
*   **Smart Polyphony**: Distinguishes chord instruments from melodic instruments
*   **Wandering Tempo**: BPM micro-drifts smoothly via Perlin noise
*   **Robust Loading**: Individual instrument loading prevents a single failure from blocking the rest

### 🌊 Auto-Drift & Zen Mode
*   **Zen Intro**: Soft, progressive 30-second start
*   **Evolving Soundscape**: Instruments added/removed based on density and spectral balance
*   **Parameter Drift**: Tension, intensity, and tempo evolve organically

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

## 📦 Project Structure (v1.19.2)
```
Quoniam/
├── ai_conductor.py      # AI Conductor (Perlin noise, phrasing, smart envelopes)
├── audio_engine.py      # SCAMP audio engine (class-based, robust loading)
├── interface.py         # Flet UI (Liquid Glass, kaleidoscope, particles)
├── config.py            # Global state & settings
├── gammes.py            # Musical scales database
├── assets_library.py    # SVG icons & visual assets
├── main.py              # Standalone engine runner
├── requirements.txt     # Dependencies
└── FluidR3_GM.sf2       # SoundFont (not included, download separately)
```
