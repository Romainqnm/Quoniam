# PROJET QUONIAM v0.5
# Module: Fusion (Harmonie + Contrôle)

from scamp import Session, wait
from pynput import keyboard
import random
import threading

# --- 1. L'ÉTAT DU SYSTÈME (La Mémoire Partagée) ---
ETAT = {
    "actif": True,
    "mode": "nuit",       # "nuit" (calme) ou "jour" (focus)
    "volume_global": 0.6
}

# --- 2. LES PALETTES SONORES ---
# Mode NUIT : Gammes mineures, basses, mystérieuses
ACCORDS_NUIT = [
    [40, 47, 52, 55], # Mi mineur sombre
    [45, 52, 57, 60], # La mineur nostalgique
    [38, 45, 50, 53], # Ré mineur profond
]

# Mode JOUR : Gammes majeures, plus aiguës, lumineuses
ACCORDS_JOUR = [
    [60, 64, 67, 72], # Do Majeur brillant
    [62, 66, 69, 74], # Ré Majeur ensoleillé
    [65, 69, 72, 77], # Fa Majeur aérien
]

# --- 3. LE CERVEAU (Gestion du Clavier) ---
def on_press(key):
    global ETAT
    try:
        if hasattr(key, 'char'):
            if key.char == '1':
                ETAT["mode"] = "nuit"
                print("\n>>> MODE NUIT ACTIVÉ (Calme, Profond)")
            elif key.char == '2':
                ETAT["mode"] = "jour"
                print("\n>>> MODE JOUR ACTIVÉ (Clarté, Focus)")
            elif key.char == 'p': # p comme pause
                pass # géré via espace ci-dessous
                
        # Gestion de la barre espace pour Pause
        if key == keyboard.Key.space:
            ETAT["actif"] = not ETAT["actif"]
            status = "LECTURE" if ETAT["actif"] else "PAUSE"
            print(f"\n>>> {status}")

    except AttributeError:
        pass

def lancer_ecoute_clavier():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# --- 4. LE CŒUR (Moteur Audio) ---
def jouer_accord(session, notes, duree_base, vitesse_arpege):
    """Joue un accord entier avec un effet de strumming (guitare/harpe)"""
    for note in notes:
        # Humanisation du volume et du timing
        vol = random.uniform(ETAT["volume_global"] - 0.1, ETAT["volume_global"] + 0.1)
        
        # On lance la note sans bloquer (fork implicite via play_note non bloquant ici ?)
        # En SCAMP, play_note est bloquant par défaut sauf si on utilise fork.
        # Ici on va tricher : on joue la note dans l'instrument principal
        # Mais comme on est DÉJÀ dans un fork (voir boucle principale), c'est bon.
        
        instrument.play_note(note, vol, duree_base, blocking=False)
        
        # Petit décalage entre les notes (arpeggiator)
        wait(random.uniform(0.05, vitesse_arpege))

# Initialisation Session Globale
s = Session(tempo=60)
instrument = s.new_part("Electric Piano")

def main():
    print("--- QUONIAM v0.5 : SYSTÈME COMPLET ---")
    print("[1] Nuit (Relaxation)")
    print("[2] Jour (Focus)")
    print("[ESPACE] Pause/Play")
    print("--------------------------------------")
    
    lancer_ecoute_clavier()
    
    while True:
        try:
            if ETAT["actif"]:
                # A. Lecture de l'état actuel pour décider quoi jouer
                mode = ETAT["mode"]
                
                if mode == "nuit":
                    choix_accords = ACCORDS_NUIT
                    vitesse = 0.3    # Arpège lent
                    attente = 4.0    # Accords espacés
                    duree_son = 6.0  # Résonance longue
                else: # jour
                    choix_accords = ACCORDS_JOUR
                    vitesse = 0.1    # Arpège rapide
                    attente = 2.0    # Accords rapprochés
                    duree_son = 3.0  # Plus court, plus sec
                
                # B. Sélection
                accord = random.choice(choix_accords)
                
                # C. Action (Fork = Parallèle)
                # On demande à SCAMP de jouer l'accord "à côté" du programme principal
                s.fork(jouer_accord, args=[s, accord, duree_son, vitesse])
                
                # D. Attente avant la prochaine vague
                wait(random.uniform(attente * 0.8, attente * 1.2))
                
            else:
                # Si en pause, on attend un peu pour économiser le CPU
                wait(0.5)
                
        except KeyboardInterrupt:
            print("\n--- ARRÊT ---")
            break

if __name__ == "__main__":
    main()