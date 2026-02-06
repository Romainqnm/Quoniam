# main.py - MOTEUR AUDIO v1.6 (GRAVITY & CHAOS)
from scamp import Session, wait
import random
import config
import gammes

def trouver_note_proche(note_actuelle, gamme, direction, facteur_chaos):
    try:
        note_ref = min(gamme, key=lambda x: abs(x - note_actuelle))
        index = gamme.index(note_ref)
        
        # Le CHAOS permet de sauter des marches (pas de 1, 2 ou 3 notes)
        saut = 1
        if random.random() * 100 < facteur_chaos:
            saut = random.randint(2, 4)
            
        nouveau_index = index + (direction * saut)
        # On garde l'index dans les limites de la liste
        nouveau_index = max(0, min(nouveau_index, len(gamme)-1))
        return gamme[nouveau_index]
    except ValueError:
        return 60

def main():
    print("--- DÉMARRAGE DU MOTEUR AUDIO v1.6 ---")
    s = Session(tempo=120)
    
    instruments = {
        "eau": s.new_part("Marimba"),
        "air": s.new_part("Electric Piano"),
        "feu": s.new_part("Acoustic Guitar")
    }
    
    print("--- PRÊT ---")
    note_courante = 60 
    
    while True:
        try:
            if not config.ETAT["actif"]:
                wait(0.1)
                continue

            # Lecture des paramètres
            preset = config.ETAT["preset"]
            vitesse = config.ETAT["vitesse"]
            intensite = config.ETAT["intensite"]
            gravite = config.ETAT["gravite"] # Valeur entre -2 et 2
            chaos = config.ETAT["chaos"]     # Valeur entre 0 et 100

            inst_actuel = instruments[preset]
            
            if preset == "eau": gamme = gammes.EAU
            elif preset == "air": gamme = gammes.AIR
            else: gamme = gammes.FEU

            # Calculs Timing
            facteur = 1.5 if preset == "air" else 1.0
            attente = (0.8 - (vitesse / 150.0)) * facteur
            if attente < 0.05: attente = 0.05

            seuil_jeu = 0.3 + (intensite / 200.0)
            
            if random.random() < seuil_jeu:
                direction = random.choice([-1, 1])
                
                # Le chaos influence aussi les changements de direction brusques
                if random.random() * 100 < chaos:
                    direction *= -1
                
                note_brute = trouver_note_proche(note_courante, gamme, direction, chaos)
                note_courante = note_brute # On mémorise la position réelle dans la gamme
                
                # APPLICATION DE LA GRAVITÉ (Pitch Shift)
                # On ajoute 12 demi-tons par niveau de gravité
                note_jouee = note_brute + (gravite * 12)
                
                vol = 0.3 + (intensite / 200.0)
                vol = random.uniform(vol - 0.1, vol + 0.1)
                overlap = 4.0 if preset == "air" else 1.2
                
                inst_actuel.play_note(note_jouee, vol, attente * overlap, blocking=False)
            
            wait(attente)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()