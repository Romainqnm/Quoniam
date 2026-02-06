# main.py - MOTEUR AUDIO v1.8 (ADAPTATIF)
from scamp import Session, wait
import random
import datetime # Pour lire l'heure
import config
import gammes

def trouver_note_proche(note_actuelle, gamme, direction, facteur_chaos):
    try:
        note_ref = min(gamme, key=lambda x: abs(x - note_actuelle))
        index = gamme.index(note_ref)
        saut = 1
        if random.random() * 100 < facteur_chaos:
            saut = random.randint(2, 4)
        nouveau_index = max(0, min(index + (direction * saut), len(gamme)-1))
        return gamme[nouveau_index]
    except ValueError:
        return 60

def gerer_mode_auto():
    """Change le preset en fonction de l'heure réelle"""
    heure = datetime.datetime.now().hour
    
    # Logique Circadienne
    if 6 <= heure < 10:   nouveau = "terre"  # Réveil calme (6h-10h)
    elif 10 <= heure < 14: nouveau = "feu"    # Productivité (10h-14h)
    elif 14 <= heure < 19: nouveau = "air"    # Flow créatif (14h-19h)
    elif 19 <= heure < 23: nouveau = "eau"    # Détente (19h-23h)
    else:                  nouveau = "espace" # Nuit profonde (23h-6h)
    
    # On applique seulement si ça change
    if config.ETAT["preset"] != nouveau:
        print(f"--- AUTO : Passage à l'ambiance {nouveau.upper()} ---")
        config.ETAT["preset"] = nouveau

def main():
    print("--- DÉMARRAGE v1.8 ---")
    s = Session(tempo=120)
    
    # NOUVELLE PALETTE D'INSTRUMENTS
    instruments = {
        "eau": s.new_part("Marimba"),
        "air": s.new_part("Electric Piano"),
        "feu": s.new_part("Acoustic Guitar"),
        "terre": s.new_part("Cello"),       # Cordes frottées graves
        "espace": s.new_part("Pad 7 (halo)") # Nappe synthétique
    }
    
    note_courante = 60 
    
    while True:
        try:
            if not config.ETAT["actif"]:
                wait(0.1)
                continue

            # --- GESTION INTELLIGENTE ---
            if config.ETAT["mode_auto"]:
                gerer_mode_auto()

            # Lecture param
            preset = config.ETAT["preset"]
            inst = instruments[preset]
            
            # Sélection Gamme
            if preset == "eau": gamme = gammes.EAU
            elif preset == "air": gamme = gammes.AIR
            elif preset == "feu": gamme = gammes.FEU
            elif preset == "terre": gamme = gammes.TERRE
            else: gamme = gammes.ESPACE

            # Paramètres dynamiques
            vitesse = config.ETAT["vitesse"]
            intensite = config.ETAT["intensite"]
            
            # Le Pad (Espace) et le Cello (Terre) sont lents par nature
            facteur_lent = 2.0 if preset in ["espace", "terre"] else 1.0
            
            attente = (0.8 - (vitesse / 150.0)) * facteur_lent
            if attente < 0.05: attente = 0.05

            seuil = 0.3 + (intensite / 200.0)
            
            if random.random() < seuil:
                direction = random.choice([-1, 1])
                if random.random() * 100 < config.ETAT["chaos"]: direction *= -1
                
                note_brute = trouver_note_proche(note_courante, gamme, direction, config.ETAT["chaos"])
                note_courante = note_brute
                
                # Gravité
                note_jouee = note_brute + (config.ETAT["gravite"] * 12)
                
                vol = 0.3 + (intensite / 200.0)
                vol = random.uniform(vol - 0.1, vol + 0.1)
                
                # Effet de "Sustain" (Résonance) selon l'instrument
                overlap = 6.0 if preset == "espace" else (3.0 if preset == "terre" else 1.2)
                
                inst.play_note(note_jouee, vol, attente * overlap, blocking=False)
            
            wait(attente)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()