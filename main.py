# main.py - MOTEUR AUDIO v4.0 (LIQUID SOUL - FINAL MIX)
# Dual Layering avec mixage équilibré : Mélodie en avant, Nappe en retrait.

from scamp import Session, wait, fork
import random
import config
import gammes

# --- OUTILS HARMONIQUES ---
def trouver_accords(note_base, gamme):
    try:
        if note_base not in gamme: return [note_base]
        idx = gamme.index(note_base)
        # Accord large et ouvert pour laisser de la place
        n1 = gamme[idx]
        n2 = gamme[(idx + 4) % len(gamme)]
        n3 = gamme[(idx + 8) % len(gamme)]
        
        if n2 < n1: n2 += 12
        if n3 < n1: n3 += 12
        
        return [n1, n2, n3]
    except:
        return [note_base]

def humaniser(valeur, taux=0.1):
    """Ajoute de l'imperfection humaine"""
    return valeur * random.uniform(1.0 - taux, 1.0 + taux)

# --- MOTEUR PRINCIPAL ---

def main():
    print("--- DÉMARRAGE LIQUID SOUL v4.0 ---")
    s = Session(tempo=120)
    
    # Le Fond Sonore (Pad Warm)
    fond_sonore = s.new_part("Pad 2 (warm)") 
    
    # Les Instruments Mélodiques
    instruments = {
        "eau": s.new_part("Marimba"),
        "air": s.new_part("Electric Piano"),
        "feu": s.new_part("Acoustic Guitar"),
        "terre": s.new_part("Cello"),
        "espace": s.new_part("Pad 7 (halo)"),
        "hiver": s.new_part("Celesta"),
        "printemps": s.new_part("Kalimba"),
        "ete": s.new_part("Steel Drums"),
        "automne": s.new_part("Shakuhachi"),
        "vide": s.new_part("Pad 3 (polysynth)")
    }
    
    # --- COUCHE 1 : LE FOND DISCRET (BACKGROUND) ---
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
            
            # Note d'ancrage grave (C3)
            note_cible = min(gamme, key=lambda x: abs(x - 48))
            
            duree = 10.0 
            # MIXAGE : Volume très faible (0.05 min à 0.2 max)
            # C'est juste une présence fantomatique
            vol = 0.05 + (intensite / 800.0) 
            
            accord = trouver_accords(note_cible, gamme)
            for n in accord:
                fond_sonore.play_note(n, vol, duree, blocking=False)
                wait(0.1)
            
            wait(duree * 0.8)

    # --- COUCHE 2 : LA MÉLODIE (LEAD) ---
    def gerer_melodie():
        note_courante = 60
        while True:
            try:
                if not config.ETAT["actif"] or config.ETAT["collection"] is None:
                    wait(0.1)
                    continue

                if config.ETAT["mode_auto"]:
                    # Logique auto simplifiée (on fait confiance à l'interface/config)
                    pass 

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
                
                # Rythme fluide
                facteur_lent = 2.0 if preset in ["espace", "vide"] else 1.0
                attente = (1.0 - (vitesse / 120.0)) * facteur_lent
                attente = max(0.1, humaniser(attente, 0.2))

                seuil_jeu = 0.35 + (intensite / 200.0)
                
                if random.random() < seuil_jeu:
                    # Mouvement mélodique (Random Walk)
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
                    
                    # MIXAGE : Volume plus présent pour la mélodie (0.25 à 0.8)
                    vol = 0.25 + (intensite / 180.0)
                    vol = humaniser(vol, 0.1)
                    
                    # Résonance (Liquid Sustain)
                    sustain = 2.5
                    
                    # Accords émotionnels (Intensité forte)
                    if intensite > 65 and random.random() < 0.35:
                        acc = trouver_accords(note_finale, gamme)
                        for n in acc:
                            wait(0.03) # Strumming
                            inst.play_note(n, vol*0.85, attente*sustain, blocking=False)
                    else:
                        inst.play_note(note_finale, vol, attente*sustain, blocking=False)

                wait(attente)
            
            except Exception as e:
                print(f"Erreur : {e}")
                wait(1.0)

    # Lancement parallèle
    fork(gerer_nappe_fond)
    gerer_melodie()

if __name__ == "__main__":
    main()