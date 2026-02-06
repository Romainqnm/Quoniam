# QUONIAM ENGINE v1.4 - LAZY LOADING
from scamp import Session, wait
import random

# --- 1. CONFIGURATION PARTAGÉE ---
ETAT = {
    "actif": True,
    "preset": "eau",
    "vitesse": 50,     
    "intensite": 30,   
}

# --- 2. DONNÉES MUSICALES (Légères, on peut les laisser ici) ---
GAMME_EAU = [48, 51, 53, 55, 58, 60, 63, 65, 67, 70, 72, 75, 77, 79, 82]
GAMME_AIR = [45, 47, 48, 52, 53, 57, 59, 60, 64, 65, 69, 71, 72, 76, 77]
GAMME_FEU = [48, 51, 53, 54, 55, 58, 60, 63, 65, 66, 67, 70, 72, 75, 77]

def trouver_note_proche(note_actuelle, gamme, direction):
    try:
        note_ref = min(gamme, key=lambda x: abs(x - note_actuelle))
        index = gamme.index(note_ref)
        nouveau_index = max(0, min(index + direction, len(gamme)-1))
        return gamme[nouveau_index]
    except ValueError:
        return 60

def main():
    print("--- DÉMARRAGE DU MOTEUR AUDIO (THREAD) ---")
    
    # --- CHARGEMENT LOURD (Déplacé ICI) ---
    # C'est maintenant que ça charge, pendant que l'interface est déjà ouverte
    s = Session(tempo=120)
    
    print("... Chargement des instruments (Patience) ...")
    instruments = {
        "eau": s.new_part("Marimba"),
        "air": s.new_part("Electric Piano"),
        "feu": s.new_part("Acoustic Guitar")
    }
    print("--- MOTEUR AUDIO PRÊT ---")

    note_courante = 60 
    
    while True:
        try:
            if not ETAT["actif"]:
                wait(0.1)
                continue

            preset_actuel = ETAT["preset"]
            valeur_vitesse = ETAT["vitesse"]
            valeur_intensite = ETAT["intensite"]

            inst_actuel = instruments[preset_actuel]
            
            if preset_actuel == "eau": gamme = GAMME_EAU
            elif preset_actuel == "air": gamme = GAMME_AIR
            else: gamme = GAMME_FEU

            # Logique de jeu
            facteur = 1.5 if preset_actuel == "air" else 1.0
            attente = (0.8 - (valeur_vitesse / 150.0)) * facteur
            if attente < 0.05: attente = 0.05

            seuil = 0.3 + (valeur_intensite / 200.0)
            
            if random.random() < seuil:
                direction = random.choice([-1, 1])
                if preset_actuel == "feu" and random.random() < 0.4: direction *= 2
                
                note_courante = trouver_note_proche(note_courante, gamme, direction)
                
                vol = 0.3 + (valeur_intensite / 200.0)
                vol = random.uniform(vol - 0.1, vol + 0.1)
                
                overlap = 4.0 if preset_actuel == "air" else 1.2
                
                inst_actuel.play_note(note_courante, vol, attente * overlap, blocking=False)
            
            wait(attente)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()