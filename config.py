# config.py - L'ÉTAT PARTAGÉ
# C'est ici que l'interface et le moteur viennent lire/écrire les réglages.

ETAT = {
    "actif": True,
    "preset": "eau",   # "eau", "feu", "air"
    "vitesse": 50,     # 0 à 100
    "intensite": 30,   # 0 à 100
}