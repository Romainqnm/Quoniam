# ai_conductor.py - AI CONDUCTOR ENGINE v18.0
"""
Chef d'orchestre virtuel basé sur le bruit de Perlin.
Remplace le système Auto-Drift aléatoire par une machine à états intelligente
garantissant la cohérence harmonique et le réalisme instrumental.
"""

import math
import random
import time

import config


# ═══════════════════════════════════════════════════════════
#  1D PERLIN NOISE (inline — no external dependency)
# ═══════════════════════════════════════════════════════════

def _hash_grad(n: int) -> float:
    """Deterministic pseudo-random gradient in [-1, 1] from integer seed."""
    n = (n * 15731 + 789221) & 0x7FFFFFFF
    n = (n * n * n * 60493) & 0x7FFFFFFF
    return (n / 0x3FFFFFFF) - 1.0


def _smoothstep(t: float) -> float:
    """Hermite smoothstep for C1-continuous interpolation."""
    return t * t * (3.0 - 2.0 * t)


def perlin_1d(t: float) -> float:
    """1D value noise with smooth interpolation. Returns [0.0, 1.0]."""
    t0 = int(math.floor(t))
    frac = t - t0
    v0 = _hash_grad(t0)
    v1 = _hash_grad(t0 + 1)
    raw = v0 + (v1 - v0) * _smoothstep(frac)  # [-1, 1]
    return (raw + 1.0) * 0.5  # normalize to [0, 1]


# ═══════════════════════════════════════════════════════════
#  AI CONDUCTOR
# ═══════════════════════════════════════════════════════════

class AIConductor:
    """
    Chef d'orchestre IA pour Quoniam.

    Gère un vecteur d'état global (tension, density, valence) qui évolue
    via du bruit de Perlin 1D, garantissant des transitions douces et organiques.

    Fonctionnalités :
    - Tessitura enforcement (plages MIDI réalistes par instrument)
    - Voice leading (conduite des voix par mouvement conjoint)
    - Scale quantization (quantification à la gamme courante)
    - Gaussian velocity humanization
    - Spectral-aware orchestration (anti-masking basses)
    - Density-driven layer management (sparse ↔ dense)
    """

    # ── Instrument Tessitura (realistic MIDI ranges) ──────────
    TESSITURA: dict[str, tuple[int, int]] = {
        "piano":       (21, 108),   # A0–C8
        "violon":      (55, 96),    # G3–C7
        "violoncelle": (36, 69),    # C2–A4
        "contrebasse": (28, 55),    # E1–G3
        "guitare":     (40, 84),    # E2–C6
        "basse":       (28, 60),    # E1–C4
        "harpe":       (24, 103),   # C1–G7
        "flute":       (60, 96),    # C4–C7
        "clarinette":  (50, 89),    # D3–F6
        "hautbois":    (58, 91),    # Bb3–G6
        "cor":         (34, 77),    # Bb1–F5
        "cuivres":     (40, 82),    # E2–Bb5
        "orgue":       (24, 96),    # C1–C7
        "timbales":    (41, 57),    # F2–A3
        "batterie":    (35, 81),    # GM drum map
        "choir":       (48, 79),    # C3–G5
        "voice":       (48, 79),    # C3–G5
        "celesta":     (60, 108),   # C4–C8
        "bells":       (60, 84),    # C4–C6
        "pizzicato":   (36, 84),    # C2–C6
    }

    # ── Spectral groups (anti-masking) ────────────────────────
    BASS_GROUP: set[str] = {"contrebasse", "basse"}
    SUB_BASS_GROUP: set[str] = {"timbales"}

    # ── Instrument categories ─────────────────────────────────
    MELODIC: set[str] = {
        "violon", "flute", "clarinette", "hautbois", "voice", "choir",
    }
    POLYPHONIC: set[str] = {
        "piano", "harpe", "guitare", "batterie",
        "celesta", "orgue", "timbales",
    }

    def __init__(self) -> None:
        # ── State vector (all 0.0–1.0) ──
        self.tension: float = 0.3
        self.density: float = 0.2
        self.valence: float = 0.5

        # ── Perlin noise time cursors (offset for independence) ──
        self._t_tension: float = random.uniform(0, 1000)
        self._t_density: float = random.uniform(0, 1000)
        self._t_valence: float = random.uniform(0, 1000)

        # ── Voice leading state: last pitch per instrument ──
        self._last_pitch: dict[str, int] = {}

        # ── Intro ramp ──
        self._start_time: float = 0.0
        self._active: bool = False

    # ═══════════════════════════════════════════════════════
    #  CORE UPDATE — called once per orchestra loop iteration
    # ═══════════════════════════════════════════════════════

    def update(self, delta: float, emotion_data: dict) -> None:
        """
        Evolve the global state vector via Perlin noise,
        map to config.ETAT, and manage instrument layers.

        Args:
            delta: Time step in beats (typically 60/bpm).
            emotion_data: Current emotion dict from config.EMOTIONS.
        """
        if not self._active:
            self._start_time = time.time()
            self._active = True

        # Advance Perlin cursors at different speeds
        self._t_tension += delta * 0.015
        self._t_density += delta * 0.012
        self._t_valence += delta * 0.008  # valence drifts slowest

        # Sample Perlin → smooth [0, 1]
        self.tension = perlin_1d(self._t_tension)
        self.density = perlin_1d(self._t_density)
        self.valence = perlin_1d(self._t_valence)

        # Intro ramp: 0 → 1 over 30 seconds
        elapsed = time.time() - self._start_time
        intro_factor = min(1.0, elapsed / 30.0)
        self.tension *= intro_factor
        self.density *= intro_factor

        # Map state → config parameters
        self._apply_to_config(emotion_data, intro_factor)

        # Manage instrument layers
        self._manage_layers(emotion_data)

    # ═══════════════════════════════════════════════════════
    #  STATE → CONFIG MAPPING
    # ═══════════════════════════════════════════════════════

    def _apply_to_config(self, emotion_data: dict, intro_factor: float) -> None:
        """Map the state vector to config.ETAT (BPM, intensity)."""
        target_bpm = emotion_data.get("bpm", 120)
        target_int = emotion_data.get("intensite", 50)

        # BPM: smooth drift ±20 around target, weighted by tension
        bpm_range = 40  # total swing
        desired_bpm = target_bpm + (self.tension - 0.5) * bpm_range
        config.ETAT["bpm"] += (desired_bpm - config.ETAT["bpm"]) * 0.03

        # Intensity: density-driven with intro ramp
        desired_int = target_int * (0.3 + 0.7 * self.density) * intro_factor
        config.ETAT["intensite"] += (desired_int - config.ETAT["intensite"]) * 0.02

    # ═══════════════════════════════════════════════════════
    #  DYNAMIC ORCHESTRATION (LAYER MANAGEMENT)
    # ═══════════════════════════════════════════════════════

    def _manage_layers(self, emotion_data: dict) -> None:
        """Add/remove instruments based on density with spectral awareness."""
        actifs = config.ETAT.get("instruments_actifs", [])
        preferred = emotion_data.get("preferred", [])
        all_available = list(self.TESSITURA.keys())

        # Target instrument count: density maps to 1–12
        target_count = max(1, int(1 + self.density * 11))

        if len(actifs) < target_count:
            # Prioritize preferred instruments
            candidates = [i for i in preferred if i not in actifs]
            if not candidates:
                candidates = [i for i in all_available if i not in actifs]
            # Spectral filter: prevent bass + sub-bass masking
            candidates = self._spectral_filter(candidates, actifs)
            if candidates:
                actifs.append(random.choice(candidates))
                config.ETAT["instruments_actifs"] = actifs
                config.ETAT["ui_needs_update"] = True

        elif len(actifs) > target_count:
            # Remove non-preferred first
            non_pref = [i for i in actifs if i not in preferred]
            bye = random.choice(non_pref) if non_pref else random.choice(actifs)
            actifs.remove(bye)
            config.ETAT["instruments_actifs"] = actifs
            config.ETAT["ui_needs_update"] = True

    def _spectral_filter(self, candidates: list[str], actifs: list[str]) -> list[str]:
        """Remove candidates that would cause frequency masking."""
        actifs_set = set(actifs)
        filtered = []
        for c in candidates:
            if c in self.BASS_GROUP and actifs_set & self.SUB_BASS_GROUP:
                continue
            if c in self.SUB_BASS_GROUP and actifs_set & self.BASS_GROUP:
                continue
            filtered.append(c)
        return filtered if filtered else candidates  # fallback: allow all

    # ═══════════════════════════════════════════════════════
    #  SCALE QUANTIZATION
    # ═══════════════════════════════════════════════════════

    def quantize_to_scale(self, pitch: int, scale: list[int]) -> int:
        """Snap pitch to nearest note in scale (multi-octave aware)."""
        if pitch in scale:
            return pitch
        best = min(scale, key=lambda n: abs(n - pitch))
        # Check octave-shifted versions for better match
        for octave_shift in (-12, 12, -24, 24):
            for n in scale:
                shifted = n + octave_shift
                if abs(shifted - pitch) < abs(best - pitch):
                    best = shifted
        return best

    # ═══════════════════════════════════════════════════════
    #  VOICE LEADING (Conjunct Motion Preference)
    # ═══════════════════════════════════════════════════════

    def voice_lead(self, inst_name: str, scale: list[int]) -> int:
        """
        Select next pitch favoring small intervals.

        - Low tension → max 3 semitones (stepwise / conjoint)
        - High tension → max 12 semitones (allows disjoint leaps)
        - Inverse-distance weighting for candidate selection
        """
        last = self._last_pitch.get(inst_name)
        if last is None:
            # First note: start from middle of tessitura
            lo, hi = self.TESSITURA.get(inst_name, (48, 72))
            mid = (lo + hi) // 2
            result = self.quantize_to_scale(mid, scale)
            result = self.clamp_tessitura(inst_name, result)
            self._last_pitch[inst_name] = result
            return result

        # Allowed interval range depends on tension
        max_interval = int(3 + self.tension * 9)

        # Gather candidate pitches within range
        candidates: list[int] = [n for n in scale if abs(n - last) <= max_interval]
        # Include octave-shifted scale degrees
        for n in scale:
            for shift in (-12, 12):
                ns = n + shift
                if abs(ns - last) <= max_interval and ns not in candidates:
                    candidates.append(ns)

        if not candidates:
            candidates = list(scale)  # fallback

        # Inverse-distance weighting: prefer smaller intervals
        weights = [1.0 / (1.0 + abs(c - last)) for c in candidates]
        total = sum(weights)
        weights = [w / total for w in weights]

        chosen = random.choices(candidates, weights=weights, k=1)[0]
        chosen = self.clamp_tessitura(inst_name, chosen)
        self._last_pitch[inst_name] = chosen
        return chosen

    # ═══════════════════════════════════════════════════════
    #  TESSITURA ENFORCEMENT
    # ═══════════════════════════════════════════════════════

    def clamp_tessitura(self, inst_name: str, pitch: int) -> int:
        """Clamp pitch to instrument's realistic MIDI range via octave wrapping."""
        lo, hi = self.TESSITURA.get(inst_name, (0, 127))
        while pitch < lo:
            pitch += 12
        while pitch > hi:
            pitch -= 12
        return max(lo, min(hi, pitch))

    # ═══════════════════════════════════════════════════════
    #  GAUSSIAN VELOCITY HUMANIZATION
    # ═══════════════════════════════════════════════════════

    def humanize_velocity(self, target: float, spread: float = 0.04) -> float:
        """
        Gaussian distribution around target volume (SCAMP 0.0–1.0 scale).
        Simulates the imperfection of a human performer.
        """
        v = random.gauss(target, spread)
        return max(0.05, min(1.0, v))

    # ═══════════════════════════════════════════════════════
    #  PER-INSTRUMENT PLAY PROBABILITY
    # ═══════════════════════════════════════════════════════

    def should_play(self, inst_name: str, emotion_data: dict) -> bool:
        """Determine if instrument should play this beat (density-aware)."""
        if inst_name in emotion_data.get("excluded", []):
            return False

        base = 0.75 if inst_name in emotion_data.get("preferred", []) else 0.5

        # Density modulates probability
        prob = base * (0.3 + 0.7 * self.density)

        # Sparse mode: melodic instruments play even less at low density
        if inst_name in self.MELODIC and self.density < 0.3:
            prob *= 0.4

        return random.random() < prob

    # ═══════════════════════════════════════════════════════
    #  DENSITY-AWARE NOTE DURATION
    # ═══════════════════════════════════════════════════════

    def suggest_duration(self, inst_name: str, rhythm: float) -> float:
        """
        Low density → long, sustained notes (sparse texture).
        High density → short, rhythmic notes (dense texture).
        """
        if inst_name in self.POLYPHONIC:
            mult = 2.0 + (1.0 - self.density) * 6.0   # 2x–8x
        else:
            mult = 1.5 + (1.0 - self.density) * 5.0   # 1.5x–6.5x
        return rhythm * mult

    # ═══════════════════════════════════════════════════════
    #  RESET (called when auto mode is toggled off)
    # ═══════════════════════════════════════════════════════

    def reset(self) -> None:
        """Reset conductor state for next activation."""
        self._active = False
        self._last_pitch.clear()
        self.tension = 0.3
        self.density = 0.2
        self.valence = 0.5
