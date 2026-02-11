# main.py - MOTEUR AUDIO v1.19.2 (ORGANIC SOUL + PHRASING)
from scamp import Session, wait, fork, Envelope
import random
import os
import time
import config
import gammes
from ai_conductor import AIConductor, SUSTAINED_INSTRUMENTS, PLUCKED_INSTRUMENTS, PERCUSSIVE_INSTRUMENTS

# --- CONFIGURATION SOUNDFONT ---
NOM_SOUNDFONT = "FluidR3_GM.sf2"

# --- OUTILS ---
def trouver_accords(note_base, gamme):
    try:
        if note_base not in gamme: return [note_base]
        idx = gamme.index(note_base)
        n1 = gamme[idx]
        n2 = gamme[(idx + 4) % len(gamme)]
        n3 = gamme[(idx + 8) % len(gamme)]
        if n2 < n1: n2 += 12
        if n3 < n1: n3 += 12
        return [n1, n2, n3]
    except:
        return [note_base]

def humaniser(valeur, taux=0.1):
    return valeur * random.uniform(1.0 - taux, 1.0 + taux)

# --- MOTEUR ---

def main():
    print("--- DÉMARRAGE LIQUID SOUL v14.4 ---")
    
    # CHARGEMENT DE LA SOUNDFONT
    # On vérifie si le fichier est là, sinon on avertit
    if os.path.exists(NOM_SOUNDFONT):
        print(f"✅ SoundFont détectée : {NOM_SOUNDFONT}")
        # On force SCAMP à utiliser ce fichier précis
        # s = Session(tempo=120, default_soundfont=NOM_SOUNDFONT) # Removed
    else:
        print(f"⚠️ ATTENTION : Fichier {NOM_SOUNDFONT} introuvable !")
        print("   -> Utilisation des sons par défaut (risque de silence).")
        print("   -> Placez le fichier .sf2 dans le même dossier que main.py")
        # s = Session(tempo=120) # Removed

    # v14.4 Rhythmic Base
    try:
        # v13.1 Fix: Standard Session Init to avoid 'fluidsynth_options' error on older SCAMP versions
        s = Session(tempo=config.ETAT["bpm"], default_soundfont=NOM_SOUNDFONT)
        print("✅ SCAMP Session démarrée (Standard Mode)")
    except Exception as e:
        print(f"⚠️ Erreur Session Init: {e}")
        s = Session(tempo=config.ETAT["bpm"], default_soundfont=NOM_SOUNDFONT)

    # INSTRUMENTS (Noms standard GM pour FluidR3)
    # FluidR3 reconnait très bien ces noms standards
    try:
        # v10.8 OPTIMIZATION: Shared Part Cache to save MIDI channels
        # SCAMP/FluidSynth is limited to 16 channels per port.
        # We reuse Parts for identical presets (e.g. Cello used in Earth and Orchestra)
        parts_cache = {}
        
        def get_part(preset_name):
            if preset_name not in parts_cache:
                try:
                    parts_cache[preset_name] = s.new_part(preset_name)
                    # print(f"🔌 New Part: {preset_name} -> Channel {parts_cache[preset_name].midi_channel}") # Removed attribute access that caused crash
                    print(f"🔌 New Part: {preset_name}") # Removed attribute access that caused crash
                except Exception as e:
                    print(f"⚠️ Failed to create part '{preset_name}': {e}")
                    return None
            return parts_cache[preset_name]

        fond_sonore = get_part("Pad 2 (warm)") 
        
        instruments = {
            # Elements (Restored v11.0)
            "eau": get_part("Marimba"),
            "air": get_part("Electric Piano 1"),
            "feu": get_part("Acoustic Guitar (nylon)"),
            "terre": get_part("Cello"),
            "espace": get_part("Pad 7 (halo)"), 
            
            # Saisons
            "hiver": get_part("Celesta"),
            "printemps": get_part("Kalimba"),
            "ete": get_part("Steel Drums"),
            "automne": get_part("Shakuhachi"),
            "vide": get_part("Pad 3 (polysynth)"),
            
            # Atmos
            "zen": get_part("Sitar"),
            "cyber": get_part("Lead 2 (sawtooth)"),
            "lofi": get_part("Electric Piano 2"),
            "jungle": get_part("Pan Flute"),
            "indus": get_part("Tubular Bells"),
            
            # Orchestra Mode — STRINGS
            "piano": get_part("Acoustic Grand Piano"),
            "violon": get_part("Violin"),
            "alto": get_part("Viola"),
            "violoncelle": get_part("Cello"),
            "contrebasse": get_part("Contrabass"),
            "guitare": get_part("Acoustic Guitar (steel)"),
            "basse": get_part("Acoustic Bass"),
            "harpe": get_part("Orchestral Harp"),
            "pizzicato": get_part("Pizzicato Strings"),
            
            # Orchestra Mode — WINDS & BRASS
            "flute": get_part("Flute"),
            "piccolo": get_part("Piccolo"),
            "clarinette": get_part("Clarinet"),
            "hautbois": get_part("Oboe"),
            "basson": get_part("Bassoon"),
            "cor": get_part("French Horn"),
            "trompette": get_part("Trumpet"),
            "cuivres": get_part("Brass Section"),
            
            # Orchestra Mode — KEYS
            "orgue": get_part("Church Organ"),
            "clavecin": get_part("Harpsichord"),
            "accordeon": get_part("Accordion"),
            
            # Orchestra Mode — PERCUSSION
            "timbales": get_part("Timpani"),
            "batterie": get_part("Orchestral Kit"),
            "xylophone": get_part("Xylophone"),
            "glockenspiel": get_part("Glockenspiel"),
            
            # Orchestra Mode — ETHEREAL & VOICES
            "choir": get_part("Choir Aahs"),
            "voice": get_part("Voice Oohs"),
            "celesta": get_part("Celesta"),
            "bells": get_part("Tubular Bells"),
        }
        
        # Filter out None values (failed parts)
        instruments = {k: v for k, v in instruments.items() if v is not None}
        print(f"✅ Loaded {len(parts_cache)} unique parts for {len(instruments)} instruments.")


        # --- AUDIO EFFECTS (CC Setup) ---
        print("🎛️  Initialisation CC (Reverb/Chorus)...")
        for name, part in instruments.items():
            try:
                # CC 91 = Reverb (General MIDI standard)
                part.play_note(0, 0, 0) # Wake up channel
                if hasattr(part, 'midi_channel') and hasattr(s, 'send_message'):
                    midi_ch = part.midi_channel
                    s.send_message(part, 176, midi_ch, 91, 95)  # type: ignore[attr-defined]  # High Reverb (Hall)
                    # CC 93 = Chorus (Ensemble effect)
                    if name in ["violon", "violoncelle", "contrebasse", "cuivres", "cor", "orgue"]:
                        s.send_message(part, 176, midi_ch, 93, 80)  # type: ignore[attr-defined]  # High Chorus
                    else:
                        s.send_message(part, 176, midi_ch, 93, 0)  # type: ignore[attr-defined]
            except: pass
    except Exception as e:
        print(f"❌ Erreur chargement instrument : {e}")
        return

    # --- COUCHE FOND ---
    def gerer_nappe_fond():
        while True:
            if not config.ETAT["actif"] or config.ETAT["collection"] is None:
                wait(1.0)
                continue
                
            # v13.0: Skip MIDI Nappe if in Audio Loop Mode
            if config.ETAT["collection"] in ["elements", "saisons", "atmos"]:
                wait(1.0)
                continue
            
            preset = config.ETAT["preset"]
            if preset is None: 
                wait(1.0)
                continue

            gamme = gammes.TOUTES_GAMMES[preset]
            intensite = config.ETAT["intensite"]
            
            note_cible = min(gamme, key=lambda x: abs(x - 48))
            duree = 10.0 
            vol = 0.05 + (intensite / 800.0) 
            
            accord = trouver_accords(note_cible, gamme)
            for n in accord:
                if fond_sonore:
                    fond_sonore.play_note(n, vol, duree, blocking=False)
                wait(0.1)
            wait(duree * 0.8)

    # --- AI CONDUCTOR (v1.19.2) ---
    conductor = AIConductor()
    print("🎼 AI Conductor initialized (Organic Soul & Phrasing)")

    # --- COUCHE MELODIE ---
    def gerer_melodie():
        note_courante = 60
        while True:
            try:
                if not config.ETAT["actif"] or config.ETAT["collection"] is None:
                    wait(0.1)
                    continue

                if config.ETAT["mode_auto"]: pass 

                # ═══════════════════════════════════════════════════════
                #  ORCHESTRA MODE v1.19.2 — ORGANIC SOUL & PHRASING
                # ═══════════════════════════════════════════════════════
                if config.ETAT.get("mode_orchestre", False):
                    actifs = config.ETAT.get("instruments_actifs", [])
                    if not actifs:
                        wait(0.5)
                        continue
                    
                    # Skip MIDI if in audio loop modes
                    current_collection = config.ETAT.get("collection")
                    if current_collection in ["elements", "saisons", "atmos"]:
                        wait(1.0)
                        continue
                    
                    # ── EMOTION ENGINE ──
                    EMOTIONS = config.EMOTIONS
                    current_emotion = config.ETAT.get("emotion", "aleatoire")
                    
                    if current_emotion == "aleatoire":
                        if "target_emotion" not in config.ETAT:
                            config.ETAT["target_emotion"] = "joyeux"
                            config.ETAT["last_emotion_switch"] = time.time()
                        if time.time() - config.ETAT.get("last_emotion_switch", 0) > random.randint(15, 25):
                            new_emotion = random.choice(list(EMOTIONS.keys()))
                            config.ETAT["target_emotion"] = new_emotion
                            config.ETAT["last_emotion_switch"] = time.time()
                        target_key = config.ETAT["target_emotion"]
                    else:
                        target_key = current_emotion
                    
                    target_data = EMOTIONS.get(target_key, EMOTIONS["joyeux"])
                    gamme = target_data["gamme"]
                    
                    # ── CONDUCTOR UPDATE (Perlin-driven state) ──
                    bpm = config.ETAT.get("bpm", 120)
                    attente = 60.0 / bpm
                    attente = humaniser(attente, 0.05)
                    
                    if config.ETAT.get("mode_auto", False):
                        conductor.update(attente, target_data)
                    
                    intensite = config.ETAT.get("intensite", 50)
                    current_time = time.time()
                    
                    # ── PLAY ALL ACTIVE INSTRUMENTS ──
                    for inst_name in list(actifs):
                        if inst_name not in instruments:
                            continue
                        if inst_name in target_data.get("excluded", []):
                            continue
                        
                        inst = instruments[inst_name]
                        
                        # ── PHRASING STATE LOGIC ──
                        # Sustained instruments: check if we should start/continue a phrase
                        is_sustained = inst_name in SUSTAINED_INSTRUMENTS
                        is_plucked = inst_name in PLUCKED_INSTRUMENTS and inst_name not in SUSTAINED_INSTRUMENTS
                        is_percussive = inst_name in PERCUSSIVE_INSTRUMENTS and inst_name not in PLUCKED_INSTRUMENTS
                        
                        in_phrase = conductor.is_in_phrase(inst_name)
                        
                        if is_sustained and not in_phrase:
                            # Not in a phrase: should we start one?
                            if conductor.should_start_phrase(inst_name):
                                conductor.begin_phrase(inst_name)
                                in_phrase = True
                            else:
                                # Not playing — sustained instruments are silent between phrases
                                continue
                        elif not is_sustained:
                            # Non-sustained: use probability-based play logic
                            if not conductor.should_play(inst_name, target_data):
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
                            pitch = conductor.voice_lead(inst_name, gamme)
                        
                        # ── DURATION (Conductor-driven) ──
                        sound_duration = conductor.suggest_duration(inst_name, attente, loop_wait=attente)
                        
                        # ── COOLDOWN UPDATE ──
                        if is_sustained and in_phrase:
                            # Legato overlap: next note available at 70-90% of duration
                            legato_wait = conductor.get_legato_wait(inst_name, sound_duration)
                            config.COOLDOWNS[inst_name] = current_time + legato_wait
                        elif inst_name in PLUCKED_INSTRUMENTS:
                            config.COOLDOWNS[inst_name] = current_time + sound_duration * 0.9
                        else:
                            config.COOLDOWNS[inst_name] = current_time + sound_duration
                        
                        # ── ANTI-MUD (don't repeat ringing pitch) ──
                        active_notes = config.ACTIVE_NOTES.get(inst_name, {})
                        if pitch in active_notes and active_notes[pitch] > current_time:
                            if random.random() < 0.7:
                                continue
                        active_notes[pitch] = current_time + sound_duration
                        config.ACTIVE_NOTES[inst_name] = {k: v for k, v in active_notes.items() if v > current_time}
                        
                        # ── VOLUME ──
                        vol = 0.15 + (intensite / 250.0)
                        vol = conductor.humanize_velocity(vol, 0.06)
                        vol = min(1.0, max(0.05, vol))
                        
                        # ── SMART ENVELOPE (per instrument family) ──
                        final_vol = conductor.get_smart_envelope(inst_name, vol, sound_duration)
                        
                        # ── PLAY NOTE ──
                        try:
                            inst.play_note(pitch, final_vol, sound_duration, blocking=False)
                        except Exception:
                            pass
                        
                        # End phrase if time is up
                        conductor.end_phrase_if_done(inst_name)
                    
                    wait(attente)
                    continue

                # STANDARD MODE LOGIC
                # v13.0: Skip standard MIDI generation for Audio Loop Modes (Elements, Seasons, Atmos)
                # This ensures only the audio file plays, not the MIDI notes.
                if config.ETAT.get("collection") in ["elements", "saisons", "atmos"]:
                    wait(1.0)
                    # Note: We rely on interface.py GlobalAudioPlayer for sound here.
                    continue

                preset = config.ETAT["preset"]
                if preset is None: 
                    wait(0.1)
                    continue

                inst = instruments[preset]
                gamme = gammes.TOUTES_GAMMES[preset]
                
                vitesse = config.ETAT["vitesse"]
                intensite = config.ETAT["intensite"]
                chaos = config.ETAT["chaos"]
                gravite = config.ETAT["gravite"]
                
                # Rythme
                presets_lents = ["espace", "vide", "indus", "zen"]
                facteur_lent = 2.0 if preset in presets_lents else 1.0
                
                attente = (1.0 - (vitesse / 120.0)) * facteur_lent
                attente = max(0.2, humaniser(attente, 0.2))

                seuil_jeu = 0.35 + (intensite / 200.0)
                
                if random.random() < seuil_jeu:
                    direction = random.choice([-1, 1])
                    if random.random() * 100 < chaos: direction *= -1
                    saut = 1
                    if random.random() * 100 < chaos: saut = random.randint(2, 4)
                    
                    try:
                        curr = min(gamme, key=lambda x: abs(x-note_courante))
                        curr_idx = gamme.index(curr)
                        new_idx = max(0, min(curr_idx + (direction*saut), len(gamme)-1))
                        note_brute = gamme[new_idx]
                    except: note_brute = 60
                    
                    note_courante = note_brute
                    note_finale = note_brute + (gravite * 12)
                    
                    vol = 0.25 + (intensite / 180.0)
                    vol = humaniser(vol, 0.15) # More humanization
                    
                    # NATURAL DECAY LOGIC
                    # Sustain is now much longer to allow fade out
                    base_sustain = 3.0 
                    if intensite > 70: base_sustain = 4.0
                    
                    # Random variation for "organic" feel
                    sustain = base_sustain * random.uniform(0.8, 1.5)
                    
                    # Occasional "staccato" (short note) based on Chaos
                    if random.random() * 100 < chaos * 0.5:
                        sustain = 0.5

                    if intensite > 65 and random.random() < 0.35:
                        acc = trouver_accords(note_finale, gamme)
                        for n in acc:
                            wait(0.1) 
                            # Non-blocking play with long sustain allows overlap
                            inst.play_note(n, vol*0.85, attente*sustain, blocking=False)
                    else:
                        inst.play_note(note_finale, vol, attente*sustain, blocking=False)

                wait(attente)
            except Exception as e:
                print(f"Erreur audio : {e}")
                wait(1.0)

    fork(gerer_nappe_fond)
    gerer_melodie()

if __name__ == "__main__":
    main()