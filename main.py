# main.py - MOTEUR AUDIO v2.2 (SMART AUTOMATION)
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
    """Applique un profil complet de réglages"""
    if config.ETAT["preset"] != preset:
        print(f"--- AUTO : Passage à {preset.upper()} ---")
        config.ETAT["preset"] = preset
    
    # On lisse les transitions (on ne change pas tout d'un coup brutalement)
    # Ici on applique directement pour l'exemple, mais on pourrait faire une interpolation
    config.ETAT["vitesse"] = vitesse
    config.ETAT["intensite"] = intensite
    config.ETAT["chaos"] = chaos
    config.ETAT["gravite"] = gravite

def gerer_mode_auto():
    """Cerveau Circadien : Adapte tout le son à l'heure"""
    heure = datetime.datetime.now().hour
    
    # MATIN (6h-10h) : Terre (Ancrage, lent mais intense)
    if 6 <= heure < 10:
        appliquer_profil("terre", vitesse=30, intensite=50, chaos=10, gravite=0)
        
    # TRAVAIL (10h-14h) : Feu (Energie, rapide, précis)
    elif 10 <= heure < 14:
        appliquer_profil("feu", vitesse=70, intensite=60, chaos=20, gravite=0)
        
    # FLOW CRÉATIF (14h-18h) : Air (Léger, rapide, un peu fou)
    elif 14 <= heure < 18:
        appliquer_profil("air", vitesse=60, intensite=40, chaos=40, gravite=1)
        
    # DÉTENTE (18h-23h) : Eau (Fluide, calme)
    elif 18 <= heure < 23:
        appliquer_profil("eau", vitesse=40, intensite=30, chaos=15, gravite=0)
        
    # NUIT PROFONDE (23h-6h) : Espace (Lent, nappes, grave et onirique)
    else:
        appliquer_profil("espace", vitesse=20, intensite=40, chaos=80, gravite=-1)

def main():
    print("--- DÉMARRAGE MOTEUR v2.2 ---")
    s = Session(tempo=120)
    
    instruments = {
        "eau": s.new_part("Marimba"),
        "air": s.new_part("Electric Piano"),
        "feu": s.new_part("Acoustic Guitar"),
        "terre": s.new_part("Cello"),
        "espace": s.new_part("Pad 7 (halo)")
    }
    
    note_courante = 60 
    
    while True:
        try:
            if not config.ETAT["actif"]:
                wait(0.1)
                continue

            # --- INTELLIGENCE ---
            if config.ETAT["mode_auto"]:
                gerer_mode_auto()

            # Lecture Données
            preset = config.ETAT["preset"]
            inst = instruments[preset]
            
            # Choix Gamme
            if preset == "eau": gamme = gammes.EAU
            elif preset == "air": gamme = gammes.AIR
            elif preset == "feu": gamme = gammes.FEU
            elif preset == "terre": gamme = gammes.TERRE
            else: gamme = gammes.ESPACE

            # Paramètres
            vitesse = config.ETAT["vitesse"]
            intensite = config.ETAT["intensite"]
            chaos = config.ETAT["chaos"]
            gravite = config.ETAT["gravite"]
            
            # Logique de jeu (inchangée mais contrôlée par l'auto)
            facteur_lent = 2.0 if preset in ["espace", "terre"] else 1.0
            attente = (0.8 - (vitesse / 150.0)) * facteur_lent
            if attente < 0.05: attente = 0.05

            seuil = 0.3 + (intensite / 200.0)
            
            if random.random() < seuil:
                direction = random.choice([-1, 1])
                if random.random() * 100 < chaos: direction *= -1
                
                note_brute = trouver_note_proche(note_courante, gamme, direction, chaos)
                note_courante = note_brute
                
                note_jouee = note_brute + (gravite * 12)
                
                vol = 0.3 + (intensite / 200.0)
                vol = random.uniform(vol - 0.1, vol + 0.1)
                
                overlap = 6.0 if preset == "espace" else (3.0 if preset == "terre" else 1.2)
                inst.play_note(note_jouee, vol, attente * overlap, blocking=False)
            
            wait(attente)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()