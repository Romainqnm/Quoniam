# config.py - v3.0
ETAT = {
    "actif": True,
    "mode_auto": False,
    
    # NAVIGATION
    "collection": None, # "elements" ou "saisons" (None = Menu Accueil)
    "preset": None,     # Sera défini quand on choisira la collection
    
    # REGLAGES SONORES
    "vitesse": 50,
    "intensite": 30,
    "gravite": 0,
    "chaos": 20,
    
    # ORCHESTRA MODE
    "mode_orchestre": False,
    "instruments_actifs": [] # Liste des instruments actifs (ex: ["piano", "violon"])
}