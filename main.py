# main.py - MOTEUR AUDIO v10.0 (LIQUID SOUL + SOUNDFONT)
from scamp import Session, wait, fork
import random
import os
import time
import config
import gammes

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
    print("--- DÉMARRAGE LIQUID SOUL v10.0 ---")
    
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

    # v10.0 Rhythmic Base
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
            "terre": get_part("Cello"), # Shared with Orchestra
            "espace": get_part("Pad 7 (halo)"), 
            
            # Saisons
            "hiver": get_part("Celesta"), # Shared with Orchestra
            "printemps": get_part("Kalimba"),
            "ete": get_part("Steel Drums"),
            "automne": get_part("Shakuhachi"),
            "vide": get_part("Pad 3 (polysynth)"),
            
            # Atmos
            "zen": get_part("Sitar"),
            "cyber": get_part("Lead 2 (sawtooth)"),
            "lofi": get_part("Electric Piano 2"),
            "jungle": get_part("Pan Flute"),
            "indus": get_part("Tubular Bells"), # Shared with Orchestra
            
            # Orchestra Mode (Real Instruments)
            "piano": get_part("Acoustic Grand Piano"),
            "violon": get_part("Violin"),
            "violoncelle": get_part("Cello"),           # Shared with 'terre'
            "contrebasse": get_part("Contrabass"),
            "flute": get_part("Flute"),
            "clarinette": get_part("Clarinet"),
            "guitare": get_part("Acoustic Guitar (steel)"),
            "basse": get_part("Acoustic Bass"),
            "harpe": get_part("Orchestral Harp"),
            # NEW INSTRUMENTS (v8.2)
            "cuivres": get_part("Brass Section"),
            "timbales": get_part("Timpani"),
            "hautbois": get_part("Oboe"),
            "cor": get_part("French Horn"),
            
            # v8.3 Additions
            "orgue": get_part("Church Organ"),
            "batterie": get_part("Orchestral Kit"), 
            
            # v10.6 ETHEREAL & VOICES
            "choir": get_part("Choir Aahs"),
            "voice": get_part("Voice Oohs"),
            "celesta": get_part("Celesta"),            # Shared with 'hiver'
            "bells": get_part("Tubular Bells"),        # Shared with 'indus'
            "pizzicato": get_part("Pizzicato Strings")
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
                s.send_message(part, 176, part.midi_channel, 91, 95) # High Reverb (Hall)
                
                # CC 93 = Chorus (Ensemble effect)
                if name in ["violon", "violoncelle", "contrebasse", "cuivres", "cor", "orgue"]:
                    s.send_message(part, 176, part.midi_channel, 93, 80) # High Chorus for ensemble/organ
                else:
                    s.send_message(part, 176, part.midi_channel, 93, 0)
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
                fond_sonore.play_note(n, vol, duree, blocking=False)
                wait(0.1)
            wait(duree * 0.8)

    # --- COUCHE MELODIE ---
    def gerer_melodie():
        note_courante = 60
        while True:
            try:
                if not config.ETAT["actif"] or config.ETAT["collection"] is None:
                    wait(0.1)
                    continue

                if config.ETAT["mode_auto"]: pass 

                # ORCHESTRA MODE LOGIC
                if config.ETAT.get("mode_orchestre", False):
                    actifs = config.ETAT.get("instruments_actifs", [])
                    if not actifs:
                        wait(0.5)
                        continue
                        
                    # --- EMOTION ENGINE (v9.0) ---
                    # Defines target parameters for each emotion
                    # --- EMOTION ENGINE (v10.4 Refactor) ---
                    # Using shared definitions from config.py for UI sync
                    EMOTIONS = config.EMOTIONS
                    
                    # DEBUG EMOTION STATE
                    # print(f"🐛 LOOP: emotion={config.ETAT.get('emotion')}, target={config.ETAT.get('target_emotion')}")

                    current_emotion = config.ETAT.get("emotion", "aleatoire")
                    
                    # Random Emotion Logic
                    if current_emotion == "aleatoire":
                        # Initialize if needed
                        if "target_emotion" not in config.ETAT:
                             config.ETAT["target_emotion"] = "joyeux"
                             config.ETAT["last_emotion_switch"] = time.time()
                        
                        # Switch every 15-25 seconds
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
                    
                    # --- INTERPOLATION LOGIC ---
                    # --- AUTO-DRIFT LOGIC (v11.0) ---
                    if config.ETAT.get("mode_auto", False):
                        curr_time = time.time()
                        start_time = config.ETAT.get("auto_start_time", 0)
                        intro_duration = 12.0 # Slow build up over 12 seconds
                        
                        # A. INTRO MODE (Progressive Intensity)
                        # If we are in the intro phase, we scale the intensity from 0 to Target
                        if curr_time - start_time < intro_duration:
                            factor = (curr_time - start_time) / intro_duration
                            target_i = target_data.get("intensite", 50)
                            # Apply scaled intensity
                            config.ETAT["intensite"] = max(10, target_i * factor) 
                            # Also force BPM to start slower? Maybe not needed.
                        
                        # B. PARAMETER DRIFT (Existing but tuned)
                        current_bpm = config.ETAT.get("bpm", 120)
                        target_bpm = target_data.get("bpm", 120)
                        if abs(current_bpm - target_bpm) > 1:
                            config.ETAT["bpm"] += (target_bpm - current_bpm) * 0.02 # Slower drift
                            
                        current_i = config.ETAT["intensite"]
                        target_i = target_data.get("intensite", 50)
                        # Only drift intensity if NOT in intro mode (or if intro finished)
                        if curr_time - start_time >= intro_duration:
                            if abs(current_i - target_i) > 1:
                                config.ETAT["intensite"] += (target_i - current_i) * 0.02

                        # C. DYNAMIC INSTRUMENT MANAGEMENT
                        # Only check every 4 seconds to avoid chaos
                        if curr_time - config.ETAT.get("last_inst_update", 0) > 4.0:
                            config.ETAT["last_inst_update"] = curr_time
                            
                            actifs = config.ETAT.get("instruments_actifs", [])
                            preferred = target_data.get("preferred", [])
                            
                            # DECISION: ADD Instrument
                            # - If very few (<3), High chance
                            # - If intro (<10s) and < 3, High chance
                            # - Random drift chance
                            should_add = False
                            if len(actifs) < 2: should_add = True
                            elif len(actifs) < 5 and random.random() < 0.3: should_add = True
                            elif random.random() < 0.1: should_add = True
                            
                            if should_add:
                                # Pick a preferred one not currently active
                                candidates = [i for i in preferred if i not in actifs]
                                # If no preferred candidates, pick any available valid instrument
                                if not candidates and random.random() < 0.2:
                                    candidates = [i for i in instruments.keys() if i not in actifs]
                                
                                if candidates:
                                    new_inst = random.choice(candidates)
                                    actifs.append(new_inst)
                                    # print(f"➕ Auto-Drift: Adding {new_inst}")
                                    config.ETAT["instruments_actifs"] = actifs
                                    config.ETAT["ui_needs_update"] = True # Signal UI

                            # DECISION: REMOVE Instrument
                            # - If too many (>6), High Chance
                            # - Random drift chance
                            should_remove = False
                            if len(actifs) > 8: should_remove = True
                            elif len(actifs) > 5 and random.random() < 0.2: should_remove = True
                            elif len(actifs) > 2 and random.random() < 0.05: should_remove = True
                            
                            if should_remove:
                                # Prioritize removing NON-preferred instruments
                                non_pref = [i for i in actifs if i not in preferred]
                                if non_pref:
                                    bye = random.choice(non_pref)
                                else:
                                    bye = random.choice(actifs)
                                
                                actifs.remove(bye)
                                # print(f"➖ Auto-Drift: Removing {bye}")
                                config.ETAT["instruments_actifs"] = actifs
                                config.ETAT["ui_needs_update"] = True # Signal UI

                    
                    
                    gamme = target_data["gamme"]
                    
                    # --- PLAYBACK LOGIC ---
                    # v13.0: Hybrid Engine (MIDI vs Audio Loop)
                    # If in Elements/Seasons/Atmos, we use Audio Loops (GlobalAudioPlayer)
                    # So we SKIP MIDI generation here, UNLESS we are in Orchestra mode (or mixed)
                    current_collection = config.ETAT.get("collection")
                    if current_collection in ["elements", "saisons", "atmos"]:
                        # MIDI Silent Mode (Audio Loop is playing in background via interface.py)
                        wait(1.0)
                        continue

                    bpm = config.ETAT.get("bpm", 120)
                    intensite = config.ETAT["intensite"]
                    chaos = config.ETAT["chaos"]
                    
                    # BPM to Seconds calculation
                    # We assume quarter note beat. attente is duration of 1 step.
                    # Base speed: 
                    attente = 60.0 / bpm
                    
                    # Humanize slightly less on rhythm to keep it tight, but still organic
                    attente = humaniser(attente, 0.05)
                    
                    # Determine next note based on random walk
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
                    
                    # Note brute before emotional pitch processing
                    note_courante = note_brute
                    
                    # Play all selected instruments (Polyrhythm chance)
                    for inst_name in actifs:
                        if inst_name in instruments:
                            
                            # v9.1 Filter: Skip excluded instruments for this emotion
                            if inst_name in target_data.get("excluded", []):
                                continue
                                
                            # v9.1 Filter: Boost presence of preferred instruments
                            threshold = 0.7
                            if inst_name in target_data.get("preferred", []):
                                threshold = 0.9 # Higher chance to play
                            
                            if random.random() < threshold: 
                                # Voice Throttling for Polyphony Safety
                                # If many instruments are active, skip some notes to prevent "Ringbuffer full"
                                density = len(actifs)
                                if density > 8 and random.random() < 0.3: continue
                                if density > 12 and random.random() < 0.5: continue

                                inst = instruments[inst_name]
                                vol = 0.2 + (intensite / 200.0)
                                vol = humaniser(vol, 0.15) 
                                
                                # Dynamic Sustain based on density to prevent polyphony overflow
                                density = len(actifs)
                                base_sustain = 2.5
                                if density > 4: base_sustain = 1.8
                                if density > 8: base_sustain = 1.2
                                
                                if inst_name in ["piano", "harpe", "guitare"]: base_sustain += 1.0
                                
                                sustain = base_sustain * random.uniform(0.8, 1.4)
                                
                                # v9.1 Logic: Emotion-based Pitch Control
                                pitch = note_courante + target_data.get("pitch_offset", 0)
                                
                                # Default instrument offsets (Bass goes low, Flute goes high)
                                if inst_name in ["contrebasse", "basse", "violoncelle", "timbales", "cuivres", "batterie"]: pitch -= 12
                                if inst_name in ["flute", "violon", "piccolo", "hautbois", "trompette"]: pitch += 12
                                
                                # v9.1 Logic: Pitch Clamping for Emotion Register
                                min_p = target_data.get("min_pitch", 0)
                                max_p = target_data.get("max_pitch", 127)
                                
                                # Smart octave shift to fit range
                                while pitch < min_p: pitch += 12
                                while pitch > max_p: pitch -= 12
                                
                                # Percussion Mapping (Drums) - unaffected by pitch logic usually
                                if inst_name == "batterie":
                                    pitch = random.choice([35, 38, 42, 46]) # Kick, Snare, HiHats
                                    sustain = 0.5
                                
                                inst.play_note(pitch, vol, attente*sustain, blocking=False)
                    
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