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
    "instruments_actifs": [], # Liste des instruments actifs (ex: ["piano", "violon"])
    
    # AUTO-DRIFT STATE (v11.0)
    "auto_start_time": 0,       # Timestamp when Auto Mode was enabled
    "last_inst_update": 0,      # Timestamp of last instrument add/remove
    
    # ZEN TIMER (v12.0)
    "timer_minutes": 0          # 0 = Disabled
}

# --- PERSISTENCE (v11.1) ---
import json
import os

PROFILES_FILE = "profiles.json"

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading profiles: {e}")
    return {}

def save_profiles_to_disk():
    try:
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(ETAT["custom_profiles"], f, indent=4)
        print(f"💾 Profiles saved to {os.path.abspath(PROFILES_FILE)}")
    except Exception as e:
        print(f"❌ Error saving profiles: {e}")

# Initialize with loaded profiles
ETAT["custom_profiles"] = load_profiles()
# EMOTION DEFINITIONS (Shared between Logic and UI)
EMOTIONS = {
    "joyeux": {
        "gamme": [60, 62, 64, 65, 67, 69, 71, 72], 
        "bpm": 110, "intensite": 70,
        "pitch_offset": 12, "min_pitch": 60, "max_pitch": 96,
        "preferred": ["flute", "violon", "piano", "harpe", "glockenspiel", "clarinette"],
        "excluded": [] # All instruments available
    }, 
    "melancolique": {
        "gamme": [60, 62, 63, 65, 67, 68, 70, 72], 
        "bpm": 60, "intensite": 40,
        "pitch_offset": 0, "min_pitch": 48, "max_pitch": 72,
        "preferred": ["violoncelle", "hautbois", "cor", "piano", "guitare"],
        "excluded": [] # All instruments available
    },
    "action": {
        "gamme": [60, 62, 63, 65, 67, 68, 71, 72], 
        "bpm": 140, "intensite": 90,
        "pitch_offset": 0, "min_pitch": 48, "max_pitch": 84,
        "preferred": ["cuivres", "timbales", "batterie", "violon", "contrebasse"],
        "excluded": [] # All instruments available
    },
    "suspense": {
        "gamme": [60, 61, 63, 64, 66, 67, 69, 70], 
        "bpm": 75, "intensite": 50,
        "pitch_offset": -12, "min_pitch": 36, "max_pitch": 64, 
        "preferred": ["contrebasse", "violoncelle", "cor", "timbales", "piano", "basse"],
        "excluded": [] # All instruments available
    },
    "epique": {
        "gamme": [60, 62, 64, 67, 69, 72, 74, 76], 
        "bpm": 100, "intensite": 95,
        "pitch_offset": 0, "min_pitch": 48, "max_pitch": 88,
        "preferred": ["cuivres", "cor", "timbales", "violon", "contrebasse", "choir"],
        "excluded": [] # No exclusions - epic uses everything
    },
    "creatif": {
        "gamme": [60, 62, 64, 65, 67, 69, 71, 72], # Major Scale default
        "bpm": 120, "intensite": 50,
        "pitch_offset": 0, "min_pitch": 0, "max_pitch": 127,
        "preferred": [],
        "excluded": [] # Nothing excluded
    },
}

