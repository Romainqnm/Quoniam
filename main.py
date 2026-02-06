# main.py - MOTEUR AUDIO v3.0 (UNIVERSAL)
from scamp import Session, wait
import random
import datetime
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

def appliquer_profil(preset, vitesse, intensite, chaos, gravite):
    if config.ETAT["preset"] != preset:
        print(f"--- AUTO : {preset.upper()} ---")
        config.ETAT["preset"] = preset
    config.ETAT["vitesse"] = vitesse
    config.ETAT["intensite"] = intensite
    config.ETAT["chaos"] = chaos
    config.ETAT["gravite"] = gravite

def gerer_mode_auto():
    heure = datetime.datetime.now().hour
    col = config.ETAT["collection"]
    
    # LOGIQUE PACK ÉLÉMENTS
    if col == "elements":
        if 6 <= heure < 10:   appliquer_profil("terre", 30, 50, 10, 0)
        elif 10 <= heure < 14: appliquer_profil("feu", 70, 60, 20, 0)
        elif 14 <= heure < 18: appliquer_profil("air", 60, 40, 40, 1)
        elif 18 <= heure < 23: appliquer_profil("eau", 40, 30, 15, 0)
        else:                  appliquer_profil("espace", 20, 40, 80, -1)

    # LOGIQUE PACK SAISONS
    elif col == "saisons":
        if 6 <= heure < 10:   appliquer_profil("printemps", 40, 40, 10, 0)
        elif 10 <= heure < 16: appliquer_profil("ete", 70, 60, 20, 0)
        elif 16 <= heure < 21: appliquer_profil("automne", 30, 50, 30, -1)
        elif 21 <= heure < 23: appliquer_profil("hiver", 20, 30, 0, 1)
        else:                  appliquer_profil("vide", 15, 40, 80, -2)

def main():
    print("--- DÉMARRAGE HUB v3.0 ---")
    s = Session(tempo=120)
    
    # CHARGEMENT MASSIF (10 Instruments)
    instruments = {
        # Pack Elements
        "eau": s.new_part("Marimba"),
        "air": s.new_part("Electric Piano"),
        "feu": s.new_part("Acoustic Guitar"),
        "terre": s.new_part("Cello"),
        "espace": s.new_part("Pad 7 (halo)"),
        
        # Pack Saisons
        "hiver": s.new_part("Celesta"),
        "printemps": s.new_part("Kalimba"),
        "ete": s.new_part("Steel Drums"),
        "automne": s.new_part("Shakuhachi"),
        "vide": s.new_part("Pad 3 (polysynth)")
    }
    
    note_courante = 60 
    
    while True:
        try:
            # Si aucun pack n'est choisi (Menu Accueil), on attend
            if config.ETAT["collection"] is None or not config.ETAT["actif"]:
                wait(0.1)
                continue

            if config.ETAT["mode_auto"]:
                gerer_mode_auto()

            preset = config.ETAT["preset"]
            
            # Sécurité si preset vide
            if preset is None: 
                wait(0.1)
                continue
                
            inst = instruments[preset]
            gamme = gammes.TOUTES_GAMMES[preset]

            # Paramètres
            vitesse = config.ETAT["vitesse"]
            intensite = config.ETAT["intensite"]
            chaos = config.ETAT["chaos"]
            gravite = config.ETAT["gravite"]
            
            # Facteurs de lenteur
            presets_lents = ["espace", "terre", "automne", "vide"]
            facteur_lent = 2.5 if preset in presets_lents else 1.0
            
            attente = (0.8 - (vitesse / 150.0)) * facteur_lent
            if attente < 0.05: attente = 0.05

            seuil = 0.3 + (intensite / 200.0)
            
            if random.random() < seuil:
                direction = random.choice([-1, 1])
                if random.random() * 100 < chaos: direction *= -1
                
                note_brute = trouver_note_proche(note_courante, gamme, direction, chaos)
                note_courante = note_brute
                
                note_jouee = note_brute + (gravite * 12)
                vol = random.uniform(max(0, (intensite/200)-0.1), min(1, (intensite/200)+0.2))
                
                overlap = 8.0 if preset == "vide" else (4.0 if preset in presets_lents else 1.2)
                
                inst.play_note(note_jouee, vol, attente * overlap, blocking=False)
            
            wait(attente)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()