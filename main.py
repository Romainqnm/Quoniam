# main.py - MOTEUR AUDIO v1.5 (MODULAIRE)
from scamp import Session, wait
import random
import config      # On importe le fichier config.py
import gammes      # On importe le fichier gammes.py

def trouver_note_proche(note_actuelle, gamme, direction):
    try:
        note_ref = min(gamme, key=lambda x: abs(x - note_actuelle))
        index = gamme.index(note_ref)
        nouveau_index = max(0, min(index + direction, len(gamme)-1))
        return gamme[nouveau_index]
    except ValueError:
        return 60

def main():
    print("--- DÉMARRAGE DU MOTEUR AUDIO ---")
    
    # Initialisation SCAMP
    s = Session(tempo=120)
    
    # Chargement des instruments
    instruments = {
        "eau": s.new_part("Marimba"),
        "air": s.new_part("Electric Piano"),
        "feu": s.new_part("Acoustic Guitar")
    }
    
    print("--- MOTEUR PRÊT ---")
    note_courante = 60 
    
    while True:
        try:
            # On lit l'état depuis le module config
            if not config.ETAT["actif"]:
                wait(0.1)
                continue

            preset_actuel = config.ETAT["preset"]
            valeur_vitesse = config.ETAT["vitesse"]
            valeur_intensite = config.ETAT["intensite"]

            inst_actuel = instruments[preset_actuel]
            
            # Sélection de la gamme via le module gammes
            if preset_actuel == "eau": gamme = gammes.EAU
            elif preset_actuel == "air": gamme = gammes.AIR
            else: gamme = gammes.FEU

            # --- Logique Audio (inchangée) ---
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