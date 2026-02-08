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
        s = Session(tempo=120, default_soundfont=NOM_SOUNDFONT)
    else:
        print(f"⚠️ ATTENTION : Fichier {NOM_SOUNDFONT} introuvable !")
        print("   -> Utilisation des sons par défaut (risque de silence).")
        print("   -> Placez le fichier .sf2 dans le même dossier que main.py")
        s = Session(tempo=120)

    # INSTRUMENTS (Noms standard GM pour FluidR3)
    # FluidR3 reconnait très bien ces noms standards
    try:
        fond_sonore = s.new_part("Pad 2 (warm)") 
        
        instruments = {
            # Elements
            "eau": s.new_part("Marimba"),
            "air": s.new_part("Electric Piano 1"),
            "feu": s.new_part("Acoustic Guitar (nylon)"),
            "terre": s.new_part("Cello"),
            "espace": s.new_part("Pad 7 (halo)"),
            
            # Saisons
            "hiver": s.new_part("Celesta"),
            "printemps": s.new_part("Kalimba"),
            "ete": s.new_part("Steel Drums"),
            "automne": s.new_part("Shakuhachi"),
            "vide": s.new_part("Pad 3 (polysynth)"),
            
            # Atmos
            "zen": s.new_part("Sitar"),
            "cyber": s.new_part("Lead 2 (sawtooth)"),
            "lofi": s.new_part("Electric Piano 2"),
            "jungle": s.new_part("Pan Flute"),
            "indus": s.new_part("Tubular Bells"),
            
            # Orchestra Mode (Real Instruments)
            "piano": s.new_part("Acoustic Grand Piano"),
            "violon": s.new_part("Violin"),
            "violoncelle": s.new_part("Cello"),
            "contrebasse": s.new_part("Contrabass"),
            "flute": s.new_part("Flute"),
            "clarinette": s.new_part("Clarinet"),
            "guitare": s.new_part("Acoustic Guitar (steel)"),
            "basse": s.new_part("Acoustic Bass"),
            "harpe": s.new_part("Orchestral Harp"),
            # NEW INSTRUMENTS (v8.2)
            "cuivres": s.new_part("Brass Section"),
            "timbales": s.new_part("Timpani"),
            "hautbois": s.new_part("Oboe"),
            "cor": s.new_part("French Horn"),
            
            # v8.3 Additions
            "orgue": s.new_part("Church Organ"),
            "batterie": s.new_part("Orchestral Kit") # Often mapped to channel 10 automatically by soundfonts
        }

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
                    EMOTIONS = {
                        "joyeux": {
                            "gamme": [60, 62, 64, 65, 67, 69, 71, 72], 
                            "bpm": 110, "intensite": 70,
                            "pitch_offset": 12, "min_pitch": 60, "max_pitch": 96,
                            "preferred": ["flute", "violon", "piano", "harpe", "glockenspiel", "clarinette"],
                            "excluded": ["contrebasse", "timbales", "tuba"]
                        }, 
                        "melancolique": {
                            "gamme": [60, 62, 63, 65, 67, 68, 70, 72], 
                            "bpm": 60, "intensite": 40,
                            "pitch_offset": 0, "min_pitch": 48, "max_pitch": 72,
                            "preferred": ["violoncelle", "hautbois", "cor", "piano", "guitare"],
                            "excluded": ["trompette", "batterie", "piccolo"]
                        },
                        "action": {
                            "gamme": [60, 62, 63, 65, 67, 68, 71, 72], 
                            "bpm": 140, "intensite": 90,
                            "pitch_offset": 0, "min_pitch": 48, "max_pitch": 84,
                            "preferred": ["cuivres", "timbales", "batterie", "violon", "contrebasse"],
                            "excluded": ["harpe", "celesta"]
                        },
                        "suspense": {
                            "gamme": [60, 61, 63, 64, 66, 67, 69, 70], 
                            "bpm": 75, "intensite": 50,
                            "pitch_offset": -12, "min_pitch": 36, "max_pitch": 64, # Low register
                            "preferred": ["contrebasse", "violoncelle", "cor", "timbales", "piano", "basse"],
                            "excluded": ["flute", "violon", "trompette", "piccolo", "celesta"]
                        },
                        "epique": {
                            "gamme": [60, 62, 64, 67, 69, 72, 74, 76], 
                            "bpm": 100, "intensite": 95,
                            "pitch_offset": 0, "min_pitch": 48, "max_pitch": 88,
                            "preferred": ["cuivres", "cor", "timbales", "violon", "contrebasse", "choir"],
                            "excluded": ["guitare", "banjo"]
                        },
                    }
                    
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
                    
                    # Smooth Interpolation (Lerp) towards Target
                    # We modify the global config to reflect the transition in UI too? 
                    # Actually, better to keep internal 'current' values separate or just direct update config for feedback?
                    # Let's update config so sliders move!
                    
                    # Smooth Interpolation (Lerp) towards Target
                    current_bpm = config.ETAT.get("bpm", 120)
                    target_bpm = target_data.get("bpm", 120)
                    
                    if abs(current_bpm - target_bpm) > 1:
                        config.ETAT["bpm"] += (target_bpm - current_bpm) * 0.05
                        
                    current_i = config.ETAT["intensite"]
                    target_i = target_data.get("intensite", 50)
                    if abs(current_i - target_i) > 1:
                        config.ETAT["intensite"] += (target_i - current_i) * 0.05
                    
                    gamme = target_data["gamme"]
                    
                    # --- PLAYBACK LOGIC ---
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
                                inst = instruments[inst_name]
                                vol = 0.2 + (intensite / 200.0)
                                vol = humaniser(vol, 0.15) 
                                
                                base_sustain = 2.5 
                                if inst_name in ["piano", "harpe", "guitare"]: base_sustain = 3.5 
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