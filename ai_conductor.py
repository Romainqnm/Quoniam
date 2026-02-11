# ai_conductor.py - AI CONDUCTOR ENGINE v1.20 (Organic Soul & Phrasing)
"""
Chef d'orchestre virtuel basé sur le bruit de Perlin.
Gère la cohérence harmonique, le réalisme instrumental,
le phrasé continu (legato), et les enveloppes physiques par famille.
"""

import math
import random
import time

import config

try:
    from scamp import Envelope
except ImportError:
    Envelope = None  # Graceful fallback


# ═══════════════════════════════════════════════════════════
#  1D PERLIN NOISE (inline — no external dependency)
# ═══════════════════════════════════════════════════════════

def _hash_grad(n: int) -> float:
    n = (n * 15731 + 789221) & 0x7FFFFFFF
    n = (n * n * n * 60493) & 0x7FFFFFFF
    return (n / 0x3FFFFFFF) - 1.0


def _smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def perlin_1d(t: float) -> float:
    t0 = int(math.floor(t))
    frac = t - t0
    v0 = _hash_grad(t0)
    v1 = _hash_grad(t0 + 1)
    raw = v0 + (v1 - v0) * _smoothstep(frac)
    return (raw + 1.0) * 0.5


# ═══════════════════════════════════════════════════════════
#  INSTRUMENT FAMILY DEFINITIONS
# ═══════════════════════════════════════════════════════════

# PERCUSSIVE: Instant attack, natural exponential decay, no sustain
# PERCUSSIVE: Instant attack, natural exponential decay, no sustain
PERCUSSIVE_INSTRUMENTS = {
    "piano", "celesta", "bells",
    "timbales", "batterie", "xylophone", "glockenspiel",
}

# SUSTAINED: Swell attack, dynamic sustain, long release tail (bowed/blown)
# These are also the CONTINUUM instruments — they weave sound non-stop.
SUSTAINED_INSTRUMENTS = {
    "violon", "violoncelle", "contrebasse", "alto",
    "flute", "clarinette", "hautbois", "cor", "cuivres",
    "basson", "trompette", "piccolo",
    "orgue", "choir", "voice",
    "accordeon",
}

# CONTINUUM instruments: silence between notes is FORBIDDEN.
# These must always overlap (tuilage). Breath only 1/10 after a long phrase.
CONTINUUM_INSTRUMENTS = {
    "violon", "alto", "violoncelle", "contrebasse",
    "flute", "clarinette", "hautbois", "basson", "piccolo",
    "cor", "cuivres", "trompette",
    "choir", "voice", "orgue", "accordeon",
}

# PLUCKED: Instant attack, short resonant decay (0.3-1.5s)
PLUCKED_INSTRUMENTS = {
    "pizzicato", "harpe", "guitare", "basse", "clavecin",
}


# ═══════════════════════════════════════════════════════════
#  AI CONDUCTOR
# ═══════════════════════════════════════════════════════════

class AIConductor:
    """
    Chef d'orchestre IA pour Quoniam v1.20 — Organic Soul.

    Three core concepts:
    1. PHRASING STATE: Legato instruments enter long phrases (15-40s)
       with note overlapping — no silence between notes.
    2. SMART ENVELOPES: Physically accurate per instrument family.
    3. LONG VARIABLE DURATIONS: Pillar notes (4-8s) + passage notes.
    """

    # ── Instrument Tessitura (realistic MIDI ranges) ──────────
    TESSITURA: dict[str, tuple[int, int]] = {
        "piano":       (21, 108),
        "violon":      (55, 96),
        "alto":        (48, 84),
        "violoncelle": (36, 69),
        "contrebasse": (28, 55),
        "guitare":     (40, 84),
        "basse":       (28, 60),
        "harpe":       (47, 95),    # Fixed: harp plays mid-high, not bass
        "flute":       (60, 96),
        "piccolo":     (74, 108),
        "clarinette":  (50, 89),
        "hautbois":    (58, 91),
        "basson":      (34, 72),
        "cor":         (34, 77),
        "trompette":   (55, 84),
        "cuivres":     (40, 82),
        "orgue":       (24, 96),
        "timbales":    (41, 57),
        "batterie":    (35, 81),
        "choir":       (48, 79),
        "voice":       (48, 79),
        "celesta":     (60, 108),
        "bells":       (60, 84),
        "pizzicato":   (48, 84),    # Fixed: mid register for plucked
        "xylophone":   (65, 96),
        "glockenspiel": (79, 108),
        "clavecin":    (29, 89),
        "clavecin":    (29, 89),
        "accordeon":   (53, 89),    # Raised bottom to F3 to avoid silent low notes
    }

    # ── Spectral groups (anti-masking) ────────────────────────
    BASS_GROUP: set[str] = {"contrebasse", "basse"}
    SUB_BASS_GROUP: set[str] = {"timbales"}

    # ── Instrument categories ─────────────────────────────────
    MELODIC: set[str] = {
        "violon", "alto", "flute", "piccolo", "clarinette",
        "hautbois", "basson", "trompette", "voice", "choir",
    }
    POLYPHONIC: set[str] = {
        "piano", "harpe", "guitare", "batterie",
        "celesta", "orgue", "timbales", "clavecin", "accordeon",
    }

    def __init__(self) -> None:
        # ── State vector (all 0.0–1.0) ──
        self.tension: float = 0.3
        self.density: float = 0.2
        self.valence: float = 0.5

        # ── Perlin noise time cursors ──
        self._t_tension: float = random.uniform(0, 1000)
        self._t_density: float = random.uniform(0, 1000)
        self._t_valence: float = random.uniform(0, 1000)

        # ── Voice leading state ──
        self._last_pitch: dict[str, int] = {}

        # ── Phrasing state per instrument ──
        self._phrase_state: dict[str, dict] = {}
        # Format: { "violon": { "active": True, "start": time, "end": time, "last_note_end": time } }

        # ── Intro ramp ──
        self._start_time: float = 0.0
        self._active: bool = False

    # ═══════════════════════════════════════════════════════
    #  PHRASING STATE SYSTEM
    # ═══════════════════════════════════════════════════════

    def get_phrase_state(self, inst_name: str) -> dict:
        """Get or create phrasing state for an instrument."""
        if inst_name not in self._phrase_state:
            self._phrase_state[inst_name] = {
                "active": False,
                "start": 0.0,
                "end": 0.0,
                "last_note_end": 0.0,
                "notes_played": 0,
            }
        return self._phrase_state[inst_name]

    def should_start_phrase(self, inst_name: str) -> bool:
        """
        Decide if this instrument should begin a new phrase.
        
        CONTINUUM RULE: For sustained instruments, the answer is
        almost ALWAYS yes. Silence is the exception, not the rule.
        Only a rare 'breath' (1/10 after a long phrase) creates a pause.
        """
        state = self.get_phrase_state(inst_name)
        now = time.time()

        # Already in a phrase → continue it
        if state["active"] and now < state["end"]:
            return False

        # ── CONTINUUM instruments: auto-restart immediately ──
        if inst_name in CONTINUUM_INSTRUMENTS:
            # Rare breath: 10% chance ONLY after a long phrase (>25s)
            phrase_len = state["end"] - state["start"] if state["end"] > 0 else 0
            if phrase_len > 25.0 and random.random() < 0.10:
                # Short breath: 1.5-3s max, then resume
                breath_end = state["end"] + random.uniform(1.5, 3.0)
                if now < breath_end:
                    return False  # Still breathing
            # Otherwise: start a new phrase NOW
            return True

        # Non-continuum sustained instruments: moderate probability
        if inst_name in SUSTAINED_INSTRUMENTS:
            prob = 0.4 + self.density * 0.4 + self.tension * 0.2
            return random.random() < prob

        # Non-sustained: probability-based
        prob = 0.15 + self.density * 0.4 + self.tension * 0.2
        return random.random() < prob

    def begin_phrase(self, inst_name: str) -> float:
        """
        Start a new phrase for this instrument.
        Returns the phrase duration.
        """
        state = self.get_phrase_state(inst_name)
        now = time.time()

        if inst_name in CONTINUUM_INSTRUMENTS:
            # Long continuous phrases: 20-60s
            duration = random.uniform(20.0, 60.0)
        elif inst_name in SUSTAINED_INSTRUMENTS:
            duration = random.uniform(15.0, 40.0)
        elif inst_name in PLUCKED_INSTRUMENTS:
            duration = random.uniform(8.0, 20.0)
        else:
            duration = random.uniform(5.0, 15.0)

        # Scale by tension: higher tension = longer phrases
        duration *= (0.7 + self.tension * 0.6)

        state["active"] = True
        state["start"] = now
        state["end"] = now + duration
        state["last_note_end"] = now
        state["notes_played"] = 0
        return duration

    def is_in_phrase(self, inst_name: str) -> bool:
        """Check if instrument is currently in an active phrase."""
        state = self.get_phrase_state(inst_name)
        return state["active"] and time.time() < state["end"]

    def end_phrase_if_done(self, inst_name: str) -> None:
        """Mark phrase as ended if time is up."""
        state = self.get_phrase_state(inst_name)
        if state["active"] and time.time() >= state["end"]:
            state["active"] = False

    # ═══════════════════════════════════════════════════════
    #  SMART ENVELOPES (Per Instrument Family)
    # ═══════════════════════════════════════════════════════

    def get_smart_envelope(self, inst_name: str, vol: float, duration: float):
        """
        Create a physically accurate SCAMP Envelope for this instrument.

        Returns an Envelope object or a float volume if Envelope unavailable.
        """
        if Envelope is None:
            return vol  # Fallback: flat volume

        try:
            # ────────────────────────────────────
            # PERCUSSIVE: Instant attack, exponential decay
            # ────────────────────────────────────
            if inst_name in PERCUSSIVE_INSTRUMENTS:
                attack = min(0.03, duration * 0.02)
                decay = duration - attack
                return Envelope.from_levels(
                    [vol, vol * 0.95, 0.0],
                    [attack, decay],
                    curve_shapes=[0, -3]
                )

            # ────────────────────────────────────
            # PLUCKED: Instant attack, resonant decay (0.5-2s)
            # ────────────────────────────────────
            if inst_name in PLUCKED_INSTRUMENTS and inst_name not in SUSTAINED_INSTRUMENTS:
                attack = 0.02
                body = duration * 0.3
                release = duration * 0.7
                return Envelope.from_levels(
                    [vol * 0.9, vol, vol * 0.4, 0.0],
                    [attack, body, release],
                    curve_shapes=[0, -2, -4]
                )

            # ────────────────────────────────────
            # SUSTAINED: Swell attack + dynamic sustain + long release
            # ────────────────────────────────────
            if inst_name in SUSTAINED_INSTRUMENTS:
                # Release tail: 1.5-2.5s (never cuts abruptly)
                release_time = min(2.5, duration * 0.15)
                release_time = max(1.0, release_time)

                # Swell: 8-15% of duration for attack
                attack_time = duration * random.uniform(0.08, 0.15)
                attack_time = max(0.3, min(2.0, attack_time))

                # Body: sustain with subtle dynamics (breathing)
                body_time = duration - attack_time - release_time

                if body_time < 0.5:
                    # Very short note: simple swell + fade
                    return Envelope.from_levels(
                        [vol * 0.1, vol, 0.0],
                        [duration * 0.3, duration * 0.7],
                        curve_shapes=[2, -3]
                    )

                # Dynamic sustain: volume breathes slightly
                peak_vol = vol * random.uniform(1.05, 1.25)
                peak_vol = min(1.0, peak_vol)
                sustain_vol = vol * random.uniform(0.75, 0.95)
                end_sustain = vol * random.uniform(0.6, 0.85)

                return Envelope.from_levels(
                    [vol * 0.05, peak_vol, sustain_vol, end_sustain, 0.0],
                    [attack_time, body_time * 0.4, body_time * 0.6, release_time],
                    curve_shapes=[3, -1, 1, -3]
                )

            # ────────────────────────────────────
            # DEFAULT: Simple swell (unknown family)
            # ────────────────────────────────────
            return Envelope.from_levels(
                [vol * 0.3, vol, 0.0],
                [duration * 0.2, duration * 0.8],
                curve_shapes=[2, -2]
            )

        except Exception:
            return vol  # Fallback on any error

    # ═══════════════════════════════════════════════════════
    #  NOTE DURATION LOGIC (Pillar + Passage)
    # ═══════════════════════════════════════════════════════

    def suggest_duration(self, inst_name: str, rhythm: float, loop_wait: float = 0.0) -> float:
        """
        Intelligent duration selection based on instrument family.

        RÈGLE D'OR (Continuum Mélodique):
        For CONTINUUM instruments, duration MUST be > loop_wait.
        This guarantees tuilage (crossfade): note A is still fading
        while note B has already begun.

        SUSTAINED instruments: Long notes (pillar 4-8s, passage 1.5-3s)
        PLUCKED instruments: Short resonant (0.3-1.5s)
        PERCUSSIVE instruments: Very short (0.1-0.5s for drums, 1-4s for piano)
        """
        if inst_name in SUSTAINED_INSTRUMENTS:
            # Pillar note (70% chance) vs passage note (30%)
            if random.random() < 0.7:
                # Pillar: 4-8 seconds
                duration = random.uniform(4.0, 8.0)
            else:
                # Passage: 1.5-3 seconds
                duration = random.uniform(1.5, 3.0)
            # Scale slightly by tension
            duration *= (0.8 + self.tension * 0.4)
            # MINIMUM: Never less than 1.5s for sustained
            duration = max(1.5, duration)

            # ── RÈGLE D'OR: duration MUST exceed loop_wait ──
            # This creates the crossfade/tuilage overlap.
            # Surplus of 25-50% ensures smooth transition.
            if inst_name in CONTINUUM_INSTRUMENTS and loop_wait > 0:
                min_duration = loop_wait * random.uniform(1.25, 1.50)
                duration = max(duration, min_duration)

            return duration

        if inst_name in PLUCKED_INSTRUMENTS:
            # Short resonant decay
            return random.uniform(0.3, 1.5)

        if inst_name == "batterie":
            return random.uniform(0.1, 0.5)

        if inst_name in PERCUSSIVE_INSTRUMENTS:
            # Melodic percussion (xylo, glock, celesta) -> short/medium
            if inst_name in {"xylophone", "glockenspiel", "timbales", "celesta"}:
                return random.uniform(0.4, 2.0)
            # Piano: medium sustain
            return random.uniform(1.0, 4.0)

        # Default
        return rhythm * random.uniform(2.0, 5.0)

    # ═══════════════════════════════════════════════════════
    #  LEGATO OVERLAP TIMING
    # ═══════════════════════════════════════════════════════

    def get_legato_wait(self, inst_name: str, note_duration: float) -> float:
        """
        For sustained instruments in a phrase: compute the wait
        before the next note. MUST be strictly < note_duration
        (this is the tuilage/crossfade guarantee).

        Returns the time to wait before playing the next note.
        """
        if inst_name in CONTINUUM_INSTRUMENTS:
            # TUILAGE: wait = 60-80% of duration.
            # This guarantees 20-40% overlap (crossfade window).
            overlap_factor = random.uniform(0.60, 0.80)
            wait = note_duration * overlap_factor
            # Hard floor: at least 0.5s to avoid machine-gun effect
            return max(0.5, wait)

        if inst_name in SUSTAINED_INSTRUMENTS:
            # Less strict overlap for non-continuum sustained
            overlap_factor = random.uniform(0.70, 0.90)
            wait = note_duration * overlap_factor
            return max(0.8, wait)

        if inst_name in PLUCKED_INSTRUMENTS:
            # Plucked: slight gap between notes
            return note_duration * random.uniform(0.8, 1.1)

        # Percussive: rhythmic, use full duration
        return note_duration

    # ═══════════════════════════════════════════════════════
    #  CORE UPDATE — called once per orchestra loop iteration
    # ═══════════════════════════════════════════════════════

    def update(self, delta: float, emotion_data: dict) -> None:
        if not self._active:
            self._start_time = time.time()
            self._active = True

        self._t_tension += delta * 0.015
        self._t_density += delta * 0.012
        self._t_valence += delta * 0.008

        self.tension = perlin_1d(self._t_tension)
        self.density = perlin_1d(self._t_density)
        self.valence = perlin_1d(self._t_valence)

        elapsed = time.time() - self._start_time
        intro_factor = min(1.0, elapsed / 30.0)
        self.tension *= intro_factor
        self.density *= intro_factor

        self._apply_to_config(emotion_data, intro_factor)
        self._manage_layers(emotion_data)

    # ═══════════════════════════════════════════════════════
    #  STATE → CONFIG MAPPING
    # ═══════════════════════════════════════════════════════

    def _apply_to_config(self, emotion_data: dict, intro_factor: float) -> None:
        target_bpm = emotion_data.get("bpm", 120)
        target_int = emotion_data.get("intensite", 50)

        bpm_range = 40
        desired_bpm = target_bpm + (self.tension - 0.5) * bpm_range
        config.ETAT["bpm"] += (desired_bpm - config.ETAT["bpm"]) * 0.03

        desired_int = target_int * (0.3 + 0.7 * self.density) * intro_factor
        config.ETAT["intensite"] += (desired_int - config.ETAT["intensite"]) * 0.02

    # ═══════════════════════════════════════════════════════
    #  DYNAMIC ORCHESTRATION
    # ═══════════════════════════════════════════════════════

    def _manage_layers(self, emotion_data: dict) -> None:
        actifs = config.ETAT.get("instruments_actifs", [])
        preferred = emotion_data.get("preferred", [])
        all_available = list(self.TESSITURA.keys())

        # Target: density maps to 1–6 (was 1-12, now more restrained)
        target_count = max(1, int(1 + self.density * 5))
        target_count = min(target_count, 6)  # Hard cap

        if len(actifs) < target_count:
            candidates = [i for i in preferred if i not in actifs]
            if not candidates:
                candidates = [i for i in all_available if i not in actifs]
            candidates = self._spectral_filter(candidates, actifs)
            if candidates:
                actifs.append(random.choice(candidates))
                config.ETAT["instruments_actifs"] = actifs
                config.ETAT["ui_needs_update"] = True

        elif len(actifs) > target_count:
            non_pref = [i for i in actifs if i not in preferred]
            bye = random.choice(non_pref) if non_pref else random.choice(actifs)
            actifs.remove(bye)
            config.ETAT["instruments_actifs"] = actifs
            config.ETAT["ui_needs_update"] = True

    def _spectral_filter(self, candidates: list[str], actifs: list[str]) -> list[str]:
        actifs_set = set(actifs)
        filtered = []
        for c in candidates:
            if c in self.BASS_GROUP and actifs_set & self.SUB_BASS_GROUP:
                continue
            if c in self.SUB_BASS_GROUP and actifs_set & self.BASS_GROUP:
                continue
            filtered.append(c)
        return filtered if filtered else candidates

    # ═══════════════════════════════════════════════════════
    #  SCALE QUANTIZATION
    # ═══════════════════════════════════════════════════════

    def quantize_to_scale(self, pitch: int, scale: list[int]) -> int:
        if pitch in scale:
            return pitch
        best = min(scale, key=lambda n: abs(n - pitch))
        for octave_shift in (-12, 12, -24, 24):
            for n in scale:
                shifted = n + octave_shift
                if abs(shifted - pitch) < abs(best - pitch):
                    best = shifted
        return best

    # ═══════════════════════════════════════════════════════
    #  VOICE LEADING
    # ═══════════════════════════════════════════════════════

    def voice_lead(self, inst_name: str, scale: list[int]) -> int:
        last = self._last_pitch.get(inst_name)
        if last is None:
            lo, hi = self.TESSITURA.get(inst_name, (48, 72))
            mid = (lo + hi) // 2
            result = self.quantize_to_scale(mid, scale)
            result = self.clamp_tessitura(inst_name, result)
            self._last_pitch[inst_name] = result
            return result

        max_interval = int(3 + self.tension * 9)
        candidates: list[int] = [n for n in scale if abs(n - last) <= max_interval]
        for n in scale:
            for shift in (-12, 12):
                ns = n + shift
                if abs(ns - last) <= max_interval and ns not in candidates:
                    candidates.append(ns)

        if not candidates:
            candidates = list(scale)

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
        v = random.gauss(target, spread)
        return max(0.05, min(1.0, v))

    # ═══════════════════════════════════════════════════════
    #  PER-INSTRUMENT PLAY PROBABILITY
    # ═══════════════════════════════════════════════════════

    def should_play(self, inst_name: str, emotion_data: dict) -> bool:
        """
        For instruments NOT in a phrase, decide if they should play.
        Instruments IN a phrase always play (handled by phrase logic).
        """
        if inst_name in emotion_data.get("excluded", []):
            return False

        # If in an active phrase, always play
        if self.is_in_phrase(inst_name):
            return True

        base = 0.55 if inst_name in emotion_data.get("preferred", []) else 0.30

        prob = base * (0.3 + 0.7 * self.density)

        if inst_name in self.MELODIC and self.density < 0.3:
            prob *= 0.4

        # BOOST: Plucked/Percussive should be more active/rhythmic
        if inst_name in PLUCKED_INSTRUMENTS or inst_name in PERCUSSIVE_INSTRUMENTS:
            prob = max(prob, 0.45)  # Ensure at least 45% chance per loop

        return random.random() < prob

    # ═══════════════════════════════════════════════════════
    #  RESET
    # ═══════════════════════════════════════════════════════

    def reset(self) -> None:
        self._active = False
        self._last_pitch.clear()
        self._phrase_state.clear()
        self.tension = 0.3
        self.density = 0.2
        self.valence = 0.5
