# audio_engine.py - MOTEUR AUDIO SCAMP REFACTORISÉ v1.19.2
"""
Moteur audio procédural basé sur SCAMP.
Génère des nappes fluides avec enveloppes dynamiques et tuilage.
"""

from scamp import Session, Envelope, wait
import random
import os
import time
import threading
from gammes import TOUTES_GAMMES
from ai_conductor import AIConductor, SUSTAINED_INSTRUMENTS, CONTINUUM_INSTRUMENTS, PLUCKED_INSTRUMENTS, PERCUSSIVE_INSTRUMENTS
import config


class QuoniamAudioEngine:
    """
    Moteur audio procédural pour Quoniam.
    Gère la génération MIDI via SCAMP avec nappes fluides et enveloppes expressives.
    """

    def __init__(self, soundfont_path="FluidR3_GM.sf2"):
        self.soundfont_path = soundfont_path
        self.session = None
        self.instruments = {}
        self.parts_cache = {}
        self.fond_sonore = None

        # État du moteur
        self.is_running = False
        self.audio_thread = None

        # État musical
        self.note_courante = 60

        # AI Conductor
        self.conductor = AIConductor()

        # Initialiser la session SCAMP
        self._init_scamp_session()

    def _init_scamp_session(self):
        """Initialise la session SCAMP et charge les instruments."""
        print("--- DÉMARRAGE LIQUID SOUL v1.19.2 (Nappes Fluides) ---")

        if os.path.exists(self.soundfont_path):
            print(f"✅ SoundFont détectée : {self.soundfont_path}")
        else:
            print(f"⚠️ ATTENTION : Fichier {self.soundfont_path} introuvable !")
            print("   -> Utilisation des sons par défaut (risque de silence).")

        # Fix #11: Session init sans retry inutile
        self.session = Session(tempo=config.ETAT["bpm"], default_soundfont=self.soundfont_path)
        print("✅ SCAMP Session initialisée")

        self._load_instruments()

    def _get_part(self, preset_name):
        """Récupère ou crée un Part SCAMP (cache pour économiser les canaux MIDI)."""
        if preset_name not in self.parts_cache:
            try:
                self.parts_cache[preset_name] = self.session.new_part(preset_name)
                print(f"🔌 New Part: {preset_name}")
            except Exception as e:
                print(f"⚠️ Failed to create part '{preset_name}': {e}")
                return None
        return self.parts_cache[preset_name]

    def _load_instruments(self):
        """Charge tous les instruments SCAMP avec effets (reverb, chorus)."""
        print("⏳ Loading instruments...")
        try:
            self.fond_sonore = self._get_part("Pad 2 (warm)")

            # Helper to safely add instruments
            def add(key, preset):
                p = self._get_part(preset)
                if p: self.instruments[key] = p

            # Éléments
            add("eau", "Marimba")
            add("air", "Electric Piano 1")
            add("feu", "Acoustic Guitar (nylon)")
            add("terre", "Cello")
            add("espace", "Pad 7 (halo)")
            
            # Saisons
            add("hiver", "Celesta")
            add("printemps", "Kalimba")
            add("ete", "Steel Drums")
            add("automne", "Shakuhachi")
            add("vide", "Pad 3 (polysynth)")
            
            # Atmosphères
            add("zen", "Sitar")
            add("cyber", "Lead 2 (sawtooth)")
            add("lofi", "Electric Piano 2")
            add("jungle", "Pan Flute")
            add("indus", "Tubular Bells")

            # Orchestre - STRINGS
            add("violon", "Violin")
            add("alto", "Viola")
            add("violoncelle", "Cello")
            add("contrebasse", "Contrabass")
            add("guitare", "Acoustic Guitar (steel)")
            add("basse", "Acoustic Bass")
            add("harpe", "Orchestral Harp")
            add("pizzicato", "Pizzicato Strings")

            # Orchestre - WINDS
            add("flute", "Flute")
            add("piccolo", "Piccolo")
            add("clarinette", "Clarinet")
            add("hautbois", "Oboe")
            add("basson", "Bassoon")
            add("cor", "French Horn")
            add("trompette", "Trumpet")
            add("cuivres", "Brass Section")

            # Orchestre - KEYS & PERC
            add("piano", "Acoustic Grand Piano")
            add("orgue", "Church Organ")
            add("clavecin", "Harpsichord")
            add("accordeon", "Accordion")
            add("timbales", "Timpani")
            add("batterie", "Orchestral Kit")
            add("xylophone", "Xylophone")
            add("glockenspiel", "Glockenspiel")

            # Orchestre - ETHEREAL
            add("choir", "Choir Aahs")
            add("voice", "Voice Oohs")
            add("celesta", "Celesta")
            add("bells", "Tubular Bells")

            print(f"✅ Loaded {len(self.parts_cache)} unique parts for {len(self.instruments)} instruments.")
            self._apply_effects()

        except Exception as e:
            # Fix #10: Halt si instruments ne chargent pas
            print(f"❌ Erreur chargement instruments : {e}")
            raise

    def _apply_effects(self):
        """Applique la réverbération et le chorus aux instruments."""
        print("🎛️  Initialisation CC (Reverb/Chorus)...")
        for name, part in self.instruments.items():
            try:
                part.play_note(0, 0, 0)  # Wake up channel
                # CC 91 = Reverb, CC 93 = Chorus
                if hasattr(part, 'midi_channel') and hasattr(self.session, 'send_message'):
                    midi_ch = part.midi_channel
                    self.session.send_message(part, 176, midi_ch, 91, 95)  # type: ignore[attr-defined]
                    if name in ["violon", "violoncelle", "contrebasse", "cuivres", "cor", "orgue"]:
                        self.session.send_message(part, 176, midi_ch, 93, 80)  # type: ignore[attr-defined]
                    else:
                        self.session.send_message(part, 176, midi_ch, 93, 0)  # type: ignore[attr-defined]
            except:
                pass

    def start(self):
        """Démarre le moteur audio dans un thread séparé."""
        if self.is_running:
            print("⚠️ Moteur déjà démarré")
            return

        self.is_running = True

        # Un seul thread Python qui héberge le contexte SCAMP.
        # wait() ne fonctionne que dans le contexte d'horloge SCAMP.
        self.audio_thread = threading.Thread(target=self._run, daemon=True)
        self.audio_thread.start()

        print("🎵 Moteur audio démarré")

    def _run(self):
        """
        Point d'entrée du thread audio.
        Exécute les boucles dans le contexte d'horloge SCAMP.
        Uses session.fork() to establish the SCAMP clock context.
        """
        self.session.fork(self._nappe_fond_loop)
        self.session.fork(self._melodie_loop)
        self.session.wait_forever()

    def stop(self):
        """Arrête le moteur audio."""
        self.is_running = False
        print("🛑 Moteur audio arrêté")

    def set_volume(self, percent):
        """Ajuste le volume global (0-100)."""
        config.ETAT["intensite"] = percent

    def set_mood(self, mood_key):
        """Change le mood/preset actuel."""
        config.ETAT["preset"] = mood_key
        print(f"🎭 Mood changé : {mood_key}")

    # ============ UTILITAIRES MUSICAUX ============

    @staticmethod
    def trouver_accords(note_base, gamme):
        """Génère une triade harmonique à partir d'une note de base."""
        try:
            if note_base not in gamme:
                return [note_base]
            idx = gamme.index(note_base)
            n1 = gamme[idx]
            n2 = gamme[(idx + 4) % len(gamme)]
            n3 = gamme[(idx + 8) % len(gamme)]
            if n2 < n1:
                n2 += 12
            if n3 < n1:
                n3 += 12
            return [n1, n2, n3]
        except:
            return [note_base]

    @staticmethod
    def humaniser(valeur, taux=0.1):
        """Ajoute une variation aléatoire pour humaniser le timing/volume."""
        return valeur * random.uniform(1.0 - taux, 1.0 + taux)

    # ============ BOUCLES AUDIO ============

    def _nappe_fond_loop(self):
        """Boucle de génération de la nappe harmonique de fond."""
        while self.is_running:
            try:
                if not config.ETAT["actif"] or config.ETAT["collection"] is None:
                    wait(1.0)
                    continue

                if config.ETAT["collection"] in ["elements", "saisons", "atmos"]:
                    wait(1.0)
                    continue

                preset = config.ETAT["preset"]
                if preset is None:
                    wait(1.0)
                    continue

                gamme = TOUTES_GAMMES.get(preset, [60, 62, 64, 65, 67, 69, 71, 72])
                intensite = config.ETAT["intensite"]

                note_cible = min(gamme, key=lambda x: abs(x - 48))
                duree = 10.0
                vol = 0.05 + (intensite / 800.0)

                accord = self.trouver_accords(note_cible, gamme)
                for n in accord:
                    if self.fond_sonore:
                        self.fond_sonore.play_note(n, vol, duree, blocking=False)
                        wait(0.1)

                wait(duree * 0.8)

            except Exception as e:
                print(f"⚠️ Erreur nappe fond: {e}")
                wait(1.0)

    def _melodie_loop(self):
        """Boucle principale de génération mélodique."""
        while self.is_running:
            try:
                if not config.ETAT["actif"] or config.ETAT["collection"] is None:
                    wait(0.1)
                    continue

                # MODE ORCHESTRE
                if config.ETAT.get("mode_orchestre", False):
                    self._play_orchestra_mode()
                    continue

                # Skip MIDI pour modes audio loop
                if config.ETAT.get("collection") in ["elements", "saisons", "atmos"]:
                    wait(1.0)
                    continue

                preset = config.ETAT["preset"]
                if preset is None:
                    wait(0.1)
                    continue

                # NAPPES FLUIDES (mode standard)
                self._play_fluid_note(preset)

            except Exception as e:
                print(f"⚠️ Erreur mélodie: {e}")
                wait(1.0)

    def _play_fluid_note(self, preset):
        """
        Joue une note avec nappe fluide :
        - Envelope avec attaque lente, sustain, relâchement lent
        - blocking=False pour parallélisation
        - wait(attente * 0.5) pour tuilage/chevauchement
        """
        inst = self.instruments.get(preset)
        if inst is None:
            wait(0.5)
            return

        gamme = TOUTES_GAMMES.get(preset, [60, 62, 64, 65, 67, 69, 71, 72])

        intensite = config.ETAT["intensite"]
        chaos = config.ETAT["chaos"]
        gravite = config.ETAT["gravite"]
        vitesse = config.ETAT.get("vitesse", 50)

        # Timing
        presets_lents = ["espace", "vide", "indus", "zen"]
        facteur_lent = 2.0 if preset in presets_lents else 1.0
        attente = (1.0 - (vitesse / 120.0)) * facteur_lent
        attente = max(0.2, self.humaniser(attente, 0.2))

        seuil_jeu = 0.35 + (intensite / 200.0)

        if random.random() < seuil_jeu:
            # Sélection de la note (random walk)
            direction = random.choice([-1, 1])
            if random.random() * 100 < chaos:
                direction *= -1

            saut = 1
            if random.random() * 100 < chaos:
                saut = random.randint(2, 4)

            try:
                curr = min(gamme, key=lambda x: abs(x - self.note_courante))
                curr_idx = gamme.index(curr)
                new_idx = max(0, min(curr_idx + (direction * saut), len(gamme) - 1))
                note_brute = gamme[new_idx]
            except:
                note_brute = 60

            self.note_courante = note_brute
            note_finale = note_brute + (gravite * 12)

            vol = 0.25 + (intensite / 180.0)
            vol = self.humaniser(vol, 0.15)

            # Fix #5: Sustain calculation fidèle à l'original
            base_sustain = 3.0
            if intensite > 70:
                base_sustain = 4.0
            sustain = base_sustain * random.uniform(0.8, 1.5)

            # Staccato occasionnel basé sur le chaos
            if random.random() * 100 < chaos * 0.5:
                sustain = 0.5

            duree_note = attente * sustain

            # Fix #7: Envelope dont la durée totale = duree_note exactement
            try:
                envelope = Envelope.from_levels(
                    [0.0, vol, vol * 0.8, 0.0],
                    [duree_note * 0.1, duree_note * 0.5, duree_note * 0.4],
                    curve_shapes=[2, 0, -2]  # type: ignore[call-arg]
                )
            except:
                envelope = vol

            # Jouer les notes
            if intensite > 65 and random.random() < 0.35:
                accord = self.trouver_accords(note_finale, gamme)
                for n in accord:
                    wait(0.1)
                    # Fix #6: Chord volume damping (vol * 0.85)
                    inst.play_note(n, vol * 0.85, duree_note, blocking=False)
            else:
                inst.play_note(note_finale, envelope, duree_note, blocking=False)

            # TUILAGE : attendre la moitié pour créer un chevauchement
            wait(attente * 0.5)
        else:
            wait(attente)

    def _play_orchestra_mode(self):
        """
        Gère la lecture en mode orchestre avec AI Conductor v1.19.2.
        ORGANIC SOUL & PHRASING + CONTINUUM MÉLODIQUE
        """
        actifs = config.ETAT.get("instruments_actifs", [])
        if not actifs:
            wait(0.5)
            return

        EMOTIONS = config.EMOTIONS
        current_emotion = config.ETAT.get("emotion", "aleatoire")

        # Random emotion switch
        if current_emotion == "aleatoire":
            if "target_emotion" not in config.ETAT:
                config.ETAT["target_emotion"] = "joyeux"
                config.ETAT["last_emotion_switch"] = time.time()

            if time.time() - config.ETAT.get("last_emotion_switch", 0) > random.randint(15, 25):
                emotions_list = list(EMOTIONS.keys())
                new_emotion = random.choice(emotions_list)
                config.ETAT["target_emotion"] = new_emotion
                config.ETAT["last_emotion_switch"] = time.time()
                print(f"🎭 Changement d'émotion : {new_emotion}")

            target_key = config.ETAT["target_emotion"]
        else:
            target_key = current_emotion

        target_data = EMOTIONS.get(target_key, EMOTIONS["joyeux"])
        gamme = target_data["gamme"]

        # Skip MIDI pour audio loop
        if config.ETAT.get("collection") in ["elements", "saisons", "atmos"]:
            wait(1.0)
            return

        bpm = config.ETAT.get("bpm", 120)
        attente = 60.0 / bpm
        attente = self.humaniser(attente, 0.05)

        # ── AI Conductor update ──
        if config.ETAT.get("mode_auto", False):
            self.conductor.update(attente, target_data)

        intensite = config.ETAT.get("intensite", 50)
        current_time = time.time()

        for inst_name in list(actifs):
            if inst_name not in self.instruments:
                continue
            if inst_name in target_data.get("excluded", []):
                continue

            inst = self.instruments[inst_name]

            # ── PHRASING STATE LOGIC ──
            # Sustained instruments: check if we should start/continue a phrase
            is_sustained = inst_name in SUSTAINED_INSTRUMENTS
            is_plucked = inst_name in PLUCKED_INSTRUMENTS and inst_name not in SUSTAINED_INSTRUMENTS
            is_percussive = inst_name in PERCUSSIVE_INSTRUMENTS and inst_name not in PLUCKED_INSTRUMENTS

            in_phrase = self.conductor.is_in_phrase(inst_name)

            if is_sustained and not in_phrase:
                # Not in a phrase: should we start one?
                # CONTINUUM RULE: should_start_phrase is almost always True for continuum instruments
                if self.conductor.should_start_phrase(inst_name):
                    self.conductor.begin_phrase(inst_name)
                    in_phrase = True
                else:
                    # Still breathing or random pause
                    continue
            elif not is_sustained:
                # Non-sustained: use probability-based play logic
                if not self.conductor.should_play(inst_name, target_data):
                    continue

            # ── COOLDOWN CHECK ──
            last_end = config.COOLDOWNS.get(inst_name, 0)
            if is_sustained and in_phrase:
                # Legato: allow heavy overlap (next note starts before prev ends)
                # Only skip if we're very early in the current note
                if current_time < last_end - 1.0:
                    continue  # Still too early, wait for overlap window
            elif not is_sustained:
                if current_time < last_end:
                    continue  # Instrument busy

            # ── PITCH (Voice Leading via Conductor) ──
            if inst_name == "batterie":
                pitch = random.choice([35, 38, 42, 46, 49])
            else:
                pitch = self.conductor.voice_lead(inst_name, gamme)

            # ── DURATION (Conductor-driven) ──
            # PASSING LOOP_WAIT (attente) IS CRITICAL FOR CONTINUUM RULE
            sound_duration = self.conductor.suggest_duration(inst_name, attente, loop_wait=attente)

            # ── COOLDOWN UPDATE ──
            if is_sustained and in_phrase:
                # Legato overlap: next note available at 60-90% of duration
                legato_wait = self.conductor.get_legato_wait(inst_name, sound_duration)
                config.COOLDOWNS[inst_name] = current_time + legato_wait
            elif inst_name in PLUCKED_INSTRUMENTS:
                config.COOLDOWNS[inst_name] = current_time + sound_duration * 0.9
            else:
                config.COOLDOWNS[inst_name] = current_time + sound_duration

            # ── ANTI-MUD (don't repeat ringing pitch) ──
            active_notes = config.ACTIVE_NOTES.get(inst_name, {})
            if pitch in active_notes and active_notes[pitch] > current_time:
                # Allow repeat for percussive sometimes
                if not is_percussive and random.random() < 0.7:
                    continue
            active_notes[pitch] = current_time + sound_duration
            config.ACTIVE_NOTES[inst_name] = {k: v for k, v in active_notes.items() if v > current_time}

            # ── VOLUME ──
            vol = 0.15 + (intensite / 250.0)
            vol = self.conductor.humanize_velocity(vol, 0.06)
            vol = min(1.0, max(0.05, vol))

            # ── SMART ENVELOPE (per instrument family) ──
            final_vol = self.conductor.get_smart_envelope(inst_name, vol, sound_duration)

            # ── PLAY NOTE ──
            try:
                inst.play_note(pitch, final_vol, sound_duration, blocking=False)
                # Count note for phrasing logic
                state = self.conductor.get_phrase_state(inst_name)
                state["notes_played"] += 1
            except Exception:
                pass

            # End phrase if time is up
            self.conductor.end_phrase_if_done(inst_name)

        wait(attente)

    def _legacy_note_select(self, gamme, target_data):
        """Original random walk note selection (non-conductor mode)."""
        chaos = config.ETAT["chaos"]
        direction = random.choice([-1, 1])
        if random.random() * 100 < chaos:
            direction *= -1
        saut = 1
        if random.random() * 100 < chaos:
            saut = random.randint(2, 4)
        try:
            curr = min(gamme, key=lambda x: abs(x - self.note_courante))
            curr_idx = gamme.index(curr)
            new_idx = max(0, min(curr_idx + (direction * saut), len(gamme) - 1))
            note_brute = gamme[new_idx]
        except:
            note_brute = 60
        self.note_courante = note_brute
        pitch = note_brute + target_data.get("pitch_offset", 0)
        min_p = target_data.get("min_pitch", 0)
        max_p = target_data.get("max_pitch", 127)
        while pitch < min_p:
            pitch += 12
        while pitch > max_p:
            pitch -= 12
        return pitch
