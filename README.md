# 🌊 QUONIAM: Fluid Dynamics Audio Engine (v14.4)

> **A procedural audio environment for focus, relaxation, and flow.**
> *Built with Python, Flet & SCAMP.*

![Quoniam Banner](Intro.png)

## 🔮 What is Quoniam?
Quoniam | Audio is a **generative audio engine** that creates infinite, non-repetitive soundscapes in real-time. Unlike a simple playlist, it uses Algorithmic Composition to generate unique melodies and harmonies on the fly, adapting to your mood and energy level.

## ✨ Key Features (v14.4)

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

### 🎛️ Audio Engine v14.4 (Liquid Soul)
A state-of-the-art procedural engine designed for organic realism:
*   **Smart Polyphony**: Distinguishes between chord instruments (Piano, Harp) and melodic instruments (Violin, Flute) to prevent muddy mixes.
*   **Infinite Sustain**: Atmospheric note decays (up to 8s) for deep immersion.
*   **Dynamic Envelopes**: Notes swell and fade organically (crescendo/decrescendo) instead of being static.
*   **Wandering Tempo**: The BPM micro-drifts (+/- 15 BPM) over time to simulate a live human performance.

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
