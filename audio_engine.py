# audio_engine.py - MOTEUR AUDIO SCAMP REFACTORISÉ v15.0
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

        # Initialiser la session SCAMP
        self._init_scamp_session()

    def _init_scamp_session(self):
        """Initialise la session SCAMP et charge les instruments."""
        print("--- DÉMARRAGE LIQUID SOUL v15.0 (Nappes Fluides) ---")

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
        try:
            self.fond_sonore = self._get_part("Pad 2 (warm)")

            self.instruments = {
                # Éléments
                "eau": self._get_part("Marimba"),
                "air": self._get_part("Electric Piano 1"),
                "feu": self._get_part("Acoustic Guitar (nylon)"),
                "terre": self._get_part("Cello"),
                "espace": self._get_part("Pad 7 (halo)"),
                # Saisons
                "hiver": self._get_part("Celesta"),
                "printemps": self._get_part("Kalimba"),
                "ete": self._get_part("Steel Drums"),
                "automne": self._get_part("Shakuhachi"),
                "vide": self._get_part("Pad 3 (polysynth)"),
                # Atmosphères
                "zen": self._get_part("Sitar"),
                "cyber": self._get_part("Lead 2 (sawtooth)"),
                "lofi": self._get_part("Electric Piano 2"),
                "jungle": self._get_part("Pan Flute"),
                "indus": self._get_part("Tubular Bells"),
                # Orchestre
                "piano": self._get_part("Acoustic Grand Piano"),
                "violon": self._get_part("Violin"),
                "violoncelle": self._get_part("Cello"),
                "contrebasse": self._get_part("Contrabass"),
                "guitare": self._get_part("Acoustic Guitar (steel)"),
                "basse": self._get_part("Acoustic Bass"),
                "harpe": self._get_part("Orchestral Harp"),
                "flute": self._get_part("Flute"),
                "clarinette": self._get_part("Clarinet"),
                "hautbois": self._get_part("Oboe"),
                "cor": self._get_part("French Horn"),
                "cuivres": self._get_part("Brass Section"),
                "orgue": self._get_part("Church Organ"),
                "timbales": self._get_part("Timpani"),
                "batterie": self._get_part("Orchestral Kit"),
                # Éthéré & Voix
                "choir": self._get_part("Choir Aahs"),
                "voice": self._get_part("Voice Oohs"),
                "celesta": self._get_part("Celesta"),
                "bells": self._get_part("Tubular Bells"),
                "pizzicato": self._get_part("Pizzicato Strings")
            }

            self.instruments = {k: v for k, v in self.instruments.items() if v is not None}
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
        """Gère la lecture en mode orchestre (logique complète conservée)."""
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

        # Auto-drift
        if config.ETAT.get("mode_auto", False):
            self._apply_auto_drift(target_data)

        gamme = target_data["gamme"]

        # Skip MIDI pour audio loop
        current_collection = config.ETAT.get("collection")
        if current_collection in ["elements", "saisons", "atmos"]:
            wait(1.0)
            return

        bpm = config.ETAT.get("bpm", 120)
        intensite = config.ETAT["intensite"]
        chaos = config.ETAT["chaos"]

        attente = 60.0 / bpm
        attente = self.humaniser(attente, 0.05)

        # Sélection de note (random walk)
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

        # Cooldowns et polyphonie

        # Fix #1: "marimba" restauré
        POLYPHONIC_INSTRUMENTS = ["piano", "harpe", "guitare", "batterie", "celesta", "marimba", "orgue", "timbales"]

        current_time = time.time()
        active_count = len(actifs)
        density_limit = 8

        for inst_name in actifs:
            if inst_name not in self.instruments:
                continue

            if inst_name in target_data.get("excluded", []):
                continue

            threshold = 0.7
            if inst_name in target_data.get("preferred", []):
                threshold = 0.9

            # Fix #3: v14.2 Auto-Drift Intro Factor
            current_intro_factor = 1.0
            if config.ETAT.get("mode_auto", False):
                intro_start = config.ETAT.get("auto_start_time", 0)
                intro_len = 30.0
                if current_time - intro_start < intro_len:
                    progress = (current_time - intro_start) / intro_len
                    current_intro_factor = max(0.1, progress)
                    # Scale probability (Density Ramp)
                    threshold = threshold * current_intro_factor

            # Fix #4: v14.2 Dynamic Expression (INST_DYNAMICS)
            current_dyn = config.INST_DYNAMICS.get(inst_name, 1.0)
            if random.random() < 0.1:
                drift = random.uniform(-0.05, 0.05)
                current_dyn = max(0.4, min(1.3, current_dyn + drift))
                config.INST_DYNAMICS[inst_name] = current_dyn

            # Cooldown check
            last_end = config.COOLDOWNS.get(inst_name, 0)
            is_polyphonic = inst_name in POLYPHONIC_INSTRUMENTS

            if not is_polyphonic:
                if current_time < last_end - 0.1:
                    continue

            # Density check
            if active_count > density_limit:
                skip_chance = 0.5 if is_polyphonic else 0.8
                if random.random() < skip_chance:
                    continue

            # Fix #3: Intro Density Check override
            if current_intro_factor < 0.5 and random.random() > current_intro_factor:
                continue

            if random.random() < threshold:
                inst = self.instruments[inst_name]
                vol = 0.2 + (intensite / 200.0)
                vol = self.humaniser(vol, 0.15)

                # Fix #4: Apply Dynamic Expression
                vol = vol * current_dyn

                # Fix #3: Apply Intro Volume Ramp
                if current_intro_factor < 1.0:
                    vol = vol * current_intro_factor

                # Pitch logic
                pitch = self.note_courante + target_data.get("pitch_offset", 0)

                # Fix #2: "piccolo" restauré dans la liste pitch-up
                if inst_name in ["contrebasse", "basse", "violoncelle", "timbales", "cuivres", "batterie"]:
                    pitch -= 12
                if inst_name in ["flute", "violon", "piccolo", "hautbois", "trompette"]:
                    pitch += 12

                # Clamping émotionnel
                min_p = target_data.get("min_pitch", 0)
                max_p = target_data.get("max_pitch", 127)
                while pitch < min_p:
                    pitch += 12
                while pitch > max_p:
                    pitch -= 12

                if inst_name == "batterie":
                    pitch = random.choice([35, 38, 42, 46])

                # Sustain / Durée
                rhythm_duration = attente
                sound_duration = attente

                if is_polyphonic:
                    sound_duration = rhythm_duration * random.uniform(3.0, 6.0)
                    config.COOLDOWNS[inst_name] = current_time + rhythm_duration
                else:
                    duration_mult = random.uniform(2.5, 8.0)
                    sound_duration = rhythm_duration * duration_mult
                    config.COOLDOWNS[inst_name] = current_time + (sound_duration * 0.95)

                # Anti-mud check
                active_notes = config.ACTIVE_NOTES.get(inst_name, {})
                if pitch in active_notes and active_notes[pitch] > current_time:
                    if random.random() < 0.8:
                        continue

                active_notes[pitch] = current_time + sound_duration
                config.ACTIVE_NOTES[inst_name] = active_notes
                config.ACTIVE_NOTES[inst_name] = {k: v for k, v in active_notes.items() if v > current_time}

                # Envelope fluide
                final_vol = vol
                if sound_duration > 1.5:
                    peak_vol = min(1.0, vol * 1.3)
                    end_vol = 0.0 if not is_polyphonic else vol * 0.2
                    try:
                        final_vol = Envelope.from_levels(
                            [vol * 0.1, peak_vol, end_vol],
                            [sound_duration * 0.4, sound_duration * 0.6],
                            curve_shapes=[3, -3]  # type: ignore[call-arg]
                        )
                    except:
                        final_vol = vol

                inst.play_note(pitch, final_vol, sound_duration, blocking=False)

        # Fix #9: Orchestra mode garde wait(attente) complet comme l'original
        wait(attente)

    def _apply_auto_drift(self, target_data):
        """Applique l'auto-drift des paramètres."""
        curr_time = time.time()
        start_time = config.ETAT.get("auto_start_time", 0)
        intro_duration = 12.0

        # Intro progressive
        if curr_time - start_time < intro_duration:
            factor = (curr_time - start_time) / intro_duration
            target_i = target_data.get("intensite", 50)
            config.ETAT["intensite"] = max(10, target_i * factor)

        # BPM micro-drift
        current_bpm = config.ETAT.get("bpm", 120)
        base_target_bpm = target_data.get("bpm", 120)

        if "bpm_micro_drift" not in config.ETAT:
            config.ETAT["bpm_micro_drift"] = 0
            config.ETAT["last_drift_update"] = 0

        if curr_time - config.ETAT.get("last_drift_update", 0) > random.randint(10, 20):
            offset = random.randint(-15, 15)
            config.ETAT["bpm_micro_drift"] = offset
            config.ETAT["last_drift_update"] = curr_time

        target_bpm = base_target_bpm + config.ETAT["bpm_micro_drift"]

        if abs(current_bpm - target_bpm) > 0.5:
            config.ETAT["bpm"] += (target_bpm - current_bpm) * 0.05

        # Intensité drift
        current_i = config.ETAT["intensite"]
        target_i = target_data.get("intensite", 50)

        if curr_time - start_time >= intro_duration:
            if abs(current_i - target_i) > 1:
                config.ETAT["intensite"] += (target_i - current_i) * 0.02

        # Gestion dynamique des instruments
        if curr_time - config.ETAT.get("last_inst_update", 0) > 4.0:
            config.ETAT["last_inst_update"] = curr_time

            actifs = config.ETAT.get("instruments_actifs", [])
            preferred = target_data.get("preferred", [])

            # Ajouter instrument
            should_add = False
            if len(actifs) < 2:
                should_add = True
            elif len(actifs) < 5 and random.random() < 0.3:
                should_add = True
            elif random.random() < 0.1:
                should_add = True

            if should_add:
                candidates = [i for i in preferred if i not in actifs]
                if not candidates and random.random() < 0.2:
                    candidates = [i for i in self.instruments.keys() if i not in actifs]

                if candidates:
                    new_inst = random.choice(candidates)
                    actifs.append(new_inst)
                    config.ETAT["instruments_actifs"] = actifs
                    config.ETAT["ui_needs_update"] = True

            # Retirer instrument
            should_remove = False
            if len(actifs) > 8:
                should_remove = True
            elif len(actifs) > 5 and random.random() < 0.2:
                should_remove = True
            elif len(actifs) > 2 and random.random() < 0.05:
                should_remove = True

            if should_remove:
                non_pref = [i for i in actifs if i not in preferred]
                if non_pref:
                    bye = random.choice(non_pref)
                else:
                    bye = random.choice(actifs)

                actifs.remove(bye)
                config.ETAT["instruments_actifs"] = actifs
                config.ETAT["ui_needs_update"] = True
