# config.py - v3.0
ETAT = {
    "actif": True,
    "mode_auto": False,
    
    # NAVIGATION
    "collection": None, # "elements" ou "saisons" (None = Menu Accueil)
    "preset": None,     # Sera défini quand on choisira la collection
    
    # REGLAGES SONORES
    "vitesse": 50, # Deprecated in v10.0 but kept for compatibility
    "bpm": 120, # v10.0 Rhythmic Base
    "intensite": 30,
    "gravite": 0,
    "chaos": 100, # Max randomness by default (v9.0)
    "emotion": "aleatoire", # v9.0 Emotional State
    "custom_profiles": {}, # v10.0 User Saved Profiles
    
    # ORCHESTRA MODE
    "mode_orchestre": False,
    "instruments_actifs": [] # Liste des instruments actifs (ex: ["piano", "violon"])
}