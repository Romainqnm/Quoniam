# main.py - MOTEUR AUDIO v4.5 (LIQUID SOUL + SOUNDFONT)
from scamp import Session, wait, fork
import random
import os
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
    print("--- DÉMARRAGE LIQUID SOUL v4.5 ---")
    
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
            "cyber": s.new_part("Lead 2 (sawtooth)"), # Modifié pour meilleure compatibilité
            "lofi": s.new_part("Electric Piano 2"),
            "jungle": s.new_part("Pan Flute"),
            "indus": s.new_part("Tubular Bells")
        }
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
                attente = max(0.1, humaniser(attente, 0.2))

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
                    vol = humaniser(vol, 0.1)
                    sustain = 2.5
                    
                    if intensite > 65 and random.random() < 0.35:
                        acc = trouver_accords(note_finale, gamme)
                        for n in acc:
                            wait(0.03)
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