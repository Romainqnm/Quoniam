# config.py - v1.20
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
    # ZEN TIMER (v12.0)
    "timer_minutes": 0          # 0 = Disabled
}

# --- AUDIO ASSETS (v13.0) ---
# Placeholder paths - User must add real files to 'assets/sounds/'
AUDIO_FILES = {
    # Elements
    "eau": "assets/sounds/rain.flac",
    "feu": "assets/sounds/fire.wav",
    "terre": "assets/sounds/forest.wav",
    "air": "assets/sounds/wind.flac",
    "espace": "assets/sounds/drone_space.wav",
    
    # Seasons
    "hiver": "assets/sounds/winter_wind.wav",
    "printemps": "assets/sounds/birds.wav",
    "ete": "assets/sounds/crickets.wav",
    "automne": "assets/sounds/rain_leaves.wav",
    "vide": "assets/sounds/white_noise.aiff",
    
    # Atmos
    "zen": "assets/sounds/bowl.wav",
    "cyber": "assets/sounds/glitchwav.wav",
    "lofi": "assets/sounds/vinyl.mp3",
    "jungle": "assets/sounds/thunder.wav",
    "indus": "assets/sounds/traffic.wav"
}

# --- PERSISTENCE (v11.1) ---
import json
import os

# Runtime state for audio engine (initialized here for Pylance)
COOLDOWNS: dict[str, float] = {}
ACTIVE_NOTES: dict[str, dict[int, float]] = {}
INST_DYNAMICS: dict[str, float] = {}

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

# --- SETTINGS (v1.20) ---
SETTINGS_DEFAULTS = {
    "fullscreen": False,
    "zen_intro": True,
    "visual_quality": "high",    # "low", "medium", "high"
    "target_fps": 30,            # 30, 60, 120, 0=unlimited
    "language": "EN",            # EN, FR, ES, AR
    "accent_color": "#00E5FF",   # Cyan default
    "export_folder": "./recordings",
}

SETTINGS = dict(SETTINGS_DEFAULTS)

# --- i18n TRANSLATIONS (v1.20) ---
TRANSLATIONS = {
    "EN": {
        # Navigation & Branding
        "main_stage": "MAIN STAGE", "atmospheres": "ATMOSPHERES",
        "elements": "ELEMENTS", "seasons": "SEASONS", "atmos": "ATMOS", "orchestra": "ORCHESTRA",
        "elements_sub": "Nature & Raw Power", "seasons_sub": "Time & Journey", "atmos_sub": "Mood & Abstraction",
        "orchestra_sub": "Compose & Conduct Harmonic Flows",
        "back": "BACK",
        # Play / Record
        "play": "PLAY", "pause": "PAUSE", "record": "Record", "stop_recording": "Stop Recording",
        "recording_saved": "Recording saved",
        # Settings dialog
        "settings": "SETTINGS", "close": "CLOSE", "reset_all": "RESET ALL",
        "settings_reset": "Settings reset to defaults",
        # Settings: Visuals
        "sec_visuals": "VISUALS", "fullscreen": "Fullscreen", "zen_intro": "Zen Intro",
        "visual_quality": "Visual Quality", "target_fps": "Target FPS",
        "low": "Low", "medium": "Medium", "high": "High", "unlimited": "Max",
        # Settings: App
        "sec_app": "APP & LOCALIZATION", "language": "Language", "accent_color": "Accent Color",
        # Settings: Data
        "sec_data": "DATA", "export_folder": "Export Folder",
        # Advanced Controls
        "advanced_controls": "Advanced Controls",
        "zen_auto": "ZEN MODE & AUTO", "auto_drift": "Auto-Drift", "sleep_timer": "Sleep Timer",
        "auto_desc": "The AI will gently drift parameters over time.",
        "rhythm_flow": "RHYTHM & FLOW", "tempo": "Tempo",
        "chaos": "Chaos", "chaos_tip": "Probability of random variations",
        "environment": "ENVIRONMENT",
        "intensity": "Intensity", "intensity_tip": "Generic density and volume of the soundscape",
        "gravity": "Gravity", "gravity_tip": "Pitch bias: High (Aer) vs Low (Earth)",
        # Instruments
        "strings": "STRINGS", "winds_brass": "WINDS & BRASS", "keys": "KEYS",
        "percussion": "PERCUSSION", "ethereal": "ETHEREAL & VOICES", "mood": "MOOD",
        # Instrument names
        "violin": "Violin", "viola": "Viola", "cello": "Cello", "contrabass": "Contrabass",
        "harp": "Harp", "guitar": "Guitar", "pizzicato": "Pizzicato", "bass": "Bass",
        "flute": "Flute", "piccolo": "Piccolo", "clarinet": "Clarinet", "oboe": "Oboe",
        "bassoon": "Bassoon", "trumpet": "Trumpet", "horn": "Horn", "brass": "Brass",
        "piano": "Piano", "organ": "Organ", "harpsichord": "Harpsichord", "accordion": "Accordion",
        "timpani": "Timpani", "drums": "Drums", "xylophone": "Xylophone", "glockenspiel": "Glockenspiel",
        "choir": "Choir", "voice": "Voice", "celesta": "Celesta", "bells": "Bells",
        # Emotions
        "random_flow": "Random Flow", "creative": "Creative Mode",
        "joy": "Joy", "melancholy": "Melancholy", "action": "Action",
        "suspense": "Suspense", "epic": "Epic",
        # Elements presets
        "earth": "Earth", "water": "Water", "fire": "Fire", "air": "Air", "space": "Space",
        # Seasons presets
        "winter": "Winter", "spring": "Spring", "summer": "Summer", "autumn": "Autumn", "void": "Void",
        # Atmos presets
        "zen": "Zen", "cyber": "Cyber", "lofi": "LoFi", "thunder": "Thunder", "traffic": "Traffic",
        # Misc
        "quit": "QUIT", "quit_tip": "Quit Application", "focus_mode": "Focus Mode",
        "exit_focus": "EXIT FOCUS", "save_profile": "SAVE PROFILE", "saved": "SAVED",
        "profile_name": "Profile Name", "cancel": "CANCEL", "save": "SAVE",
        "mute": "Mute/Unmute", "ambience_vol": "Ambience Volume",
        "zen_finished": "Zen Session Finished", "zen_set": "Zen Timer set for",
        "off": "Off",
    },
    "FR": {
        "main_stage": "SCENE PRINCIPALE", "atmospheres": "ATMOSPHERES",
        "elements": "ELEMENTS", "seasons": "SAISONS", "atmos": "ATMOS", "orchestra": "ORCHESTRE",
        "elements_sub": "Nature & Force Brute", "seasons_sub": "Temps & Voyage", "atmos_sub": "Humeur & Abstraction",
        "orchestra_sub": "Composez & Dirigez des Flux Harmoniques",
        "back": "RETOUR",
        "play": "JOUER", "pause": "PAUSE", "record": "Enregistrer", "stop_recording": "Arreter",
        "recording_saved": "Enregistrement sauvegarde",
        "settings": "PARAMETRES", "close": "FERMER", "reset_all": "REINITIALISER",
        "settings_reset": "Parametres reinitialises",
        "sec_visuals": "VISUELS", "fullscreen": "Plein Ecran", "zen_intro": "Intro Zen",
        "visual_quality": "Qualite Visuelle", "target_fps": "FPS Cible",
        "low": "Bas", "medium": "Moyen", "high": "Haut", "unlimited": "Max",
        "sec_app": "APP & LANGUE", "language": "Langue", "accent_color": "Couleur d'Accent",
        "sec_data": "DONNEES", "export_folder": "Dossier d'Export",
        "advanced_controls": "Controles Avances",
        "zen_auto": "MODE ZEN & AUTO", "auto_drift": "Derive Auto", "sleep_timer": "Minuterie",
        "auto_desc": "L'IA fera deriver les parametres doucement.",
        "rhythm_flow": "RYTHME & FLUX", "tempo": "Tempo",
        "chaos": "Chaos", "chaos_tip": "Probabilite de variations aleatoires",
        "environment": "ENVIRONNEMENT",
        "intensity": "Intensite", "intensity_tip": "Densite et volume global",
        "gravity": "Gravite", "gravity_tip": "Biais de hauteur : Aigu (Air) vs Grave (Terre)",
        "strings": "CORDES", "winds_brass": "VENTS & CUIVRES", "keys": "CLAVIERS",
        "percussion": "PERCUSSION", "ethereal": "ETHEREEL & VOIX", "mood": "HUMEUR",
        "violin": "Violon", "viola": "Alto", "cello": "Violoncelle", "contrabass": "Contrebasse",
        "harp": "Harpe", "guitar": "Guitare", "pizzicato": "Pizzicato", "bass": "Basse",
        "flute": "Flute", "piccolo": "Piccolo", "clarinet": "Clarinette", "oboe": "Hautbois",
        "bassoon": "Basson", "trumpet": "Trompette", "horn": "Cor", "brass": "Cuivres",
        "piano": "Piano", "organ": "Orgue", "harpsichord": "Clavecin", "accordion": "Accordeon",
        "timpani": "Timbales", "drums": "Batterie", "xylophone": "Xylophone", "glockenspiel": "Glockenspiel",
        "choir": "Choeur", "voice": "Voix", "celesta": "Celesta", "bells": "Cloches",
        "random_flow": "Flux Aleatoire", "creative": "Mode Creatif",
        "joy": "Joie", "melancholy": "Melancolie", "action": "Action",
        "suspense": "Suspense", "epic": "Epique",
        "earth": "Terre", "water": "Eau", "fire": "Feu", "air": "Air", "space": "Espace",
        "winter": "Hiver", "spring": "Printemps", "summer": "Ete", "autumn": "Automne", "void": "Vide",
        "zen": "Zen", "cyber": "Cyber", "lofi": "LoFi", "thunder": "Tonnerre", "traffic": "Trafic",
        "quit": "QUITTER", "quit_tip": "Quitter l'Application", "focus_mode": "Mode Focus",
        "exit_focus": "QUITTER FOCUS", "save_profile": "SAUVEGARDER", "saved": "SAUVE",
        "profile_name": "Nom du Profil", "cancel": "ANNULER", "save": "SAUVER",
        "mute": "Couper/Activer", "ambience_vol": "Volume Ambiance",
        "zen_finished": "Session Zen Terminee", "zen_set": "Minuterie Zen reglee sur",
        "off": "Off",
    },
    "ES": {
        "main_stage": "ESCENARIO", "atmospheres": "ATMOSFERAS",
        "elements": "ELEMENTOS", "seasons": "ESTACIONES", "atmos": "ATMOS", "orchestra": "ORQUESTA",
        "elements_sub": "Naturaleza & Fuerza Bruta", "seasons_sub": "Tiempo & Viaje", "atmos_sub": "Estado & Abstraccion",
        "orchestra_sub": "Compone & Dirige Flujos Armonicos",
        "back": "VOLVER",
        "play": "REPRODUCIR", "pause": "PAUSA", "record": "Grabar", "stop_recording": "Detener",
        "recording_saved": "Grabacion guardada",
        "settings": "AJUSTES", "close": "CERRAR", "reset_all": "REINICIAR",
        "settings_reset": "Ajustes restablecidos",
        "sec_visuals": "VISUALES", "fullscreen": "Pantalla Completa", "zen_intro": "Intro Zen",
        "visual_quality": "Calidad Visual", "target_fps": "FPS Objetivo",
        "low": "Bajo", "medium": "Medio", "high": "Alto", "unlimited": "Max",
        "sec_app": "APP & IDIOMA", "language": "Idioma", "accent_color": "Color de Acento",
        "sec_data": "DATOS", "export_folder": "Carpeta de Exportacion",
        "advanced_controls": "Controles Avanzados",
        "zen_auto": "MODO ZEN & AUTO", "auto_drift": "Deriva Auto", "sleep_timer": "Temporizador",
        "auto_desc": "La IA hara derivar los parametros suavemente.",
        "rhythm_flow": "RITMO & FLUJO", "tempo": "Tempo",
        "chaos": "Caos", "chaos_tip": "Probabilidad de variaciones aleatorias",
        "environment": "ENTORNO",
        "intensity": "Intensidad", "intensity_tip": "Densidad y volumen general",
        "gravity": "Gravedad", "gravity_tip": "Sesgo de tono: Agudo (Aire) vs Grave (Tierra)",
        "strings": "CUERDAS", "winds_brass": "VIENTOS & METALES", "keys": "TECLADOS",
        "percussion": "PERCUSION", "ethereal": "ETEREO & VOCES", "mood": "ANIMO",
        "violin": "Violin", "viola": "Viola", "cello": "Violonchelo", "contrabass": "Contrabajo",
        "harp": "Arpa", "guitar": "Guitarra", "pizzicato": "Pizzicato", "bass": "Bajo",
        "flute": "Flauta", "piccolo": "Piccolo", "clarinet": "Clarinete", "oboe": "Oboe",
        "bassoon": "Fagot", "trumpet": "Trompeta", "horn": "Trompa", "brass": "Metales",
        "piano": "Piano", "organ": "Organo", "harpsichord": "Clavecin", "accordion": "Acordeon",
        "timpani": "Timbales", "drums": "Bateria", "xylophone": "Xilofono", "glockenspiel": "Glockenspiel",
        "choir": "Coro", "voice": "Voz", "celesta": "Celesta", "bells": "Campanas",
        "random_flow": "Flujo Aleatorio", "creative": "Modo Creativo",
        "joy": "Alegria", "melancholy": "Melancolia", "action": "Accion",
        "suspense": "Suspenso", "epic": "Epico",
        "earth": "Tierra", "water": "Agua", "fire": "Fuego", "air": "Aire", "space": "Espacio",
        "winter": "Invierno", "spring": "Primavera", "summer": "Verano", "autumn": "Otono", "void": "Vacio",
        "zen": "Zen", "cyber": "Cyber", "lofi": "LoFi", "thunder": "Trueno", "traffic": "Trafico",
        "quit": "SALIR", "quit_tip": "Salir de la Aplicacion", "focus_mode": "Modo Enfoque",
        "exit_focus": "SALIR ENFOQUE", "save_profile": "GUARDAR PERFIL", "saved": "GUARDADO",
        "profile_name": "Nombre del Perfil", "cancel": "CANCELAR", "save": "GUARDAR",
        "mute": "Silenciar", "ambience_vol": "Volumen Ambiente",
        "zen_finished": "Sesion Zen Terminada", "zen_set": "Temporizador Zen ajustado a",
        "off": "Off",
    },
    "AR": {
        "main_stage": "ALMASRAH", "atmospheres": "ALAJWAA",
        "elements": "ALANASIR", "seasons": "ALFUSUL", "atmos": "AJWAA", "orchestra": "ALORCHESTRA",
        "elements_sub": "Tabi'a wa Quwwa", "seasons_sub": "Zaman wa Rihla", "atmos_sub": "Mzaj wa Tajrid",
        "orchestra_sub": "Allif wa Qud Tadaffuqat Harmoniyya",
        "back": "RUJU'",
        "play": "TASHGHIL", "pause": "IIQAF", "record": "Tasjil", "stop_recording": "Iiqaf Tasjil",
        "recording_saved": "Tasjil mahfuz",
        "settings": "ALI'DADAT", "close": "IGHLAQ", "reset_all": "I'ADAT DABT",
        "settings_reset": "Tamma i'adat al-i'dadat",
        "sec_visuals": "ALMAR'IYYAT", "fullscreen": "Sha-sha Kamila", "zen_intro": "Muqaddima Zen",
        "visual_quality": "Jawdat Almar'iyyat", "target_fps": "FPS Alhadaf",
        "low": "Munkhafid", "medium": "Mutawassit", "high": "Ali", "unlimited": "Aqsa",
        "sec_app": "ALTATBIQ & ALLUGHA", "language": "Allugha", "accent_color": "Lawn Alta'kid",
        "sec_data": "ALBYANAT", "export_folder": "Mujallad Altasdir",
        "advanced_controls": "Altahakkum Almutaqaddim",
        "zen_auto": "WADH ZEN & TALQA'I", "auto_drift": "Inhiraf Talqa'i", "sleep_timer": "Muaqqit Nawm",
        "auto_desc": "Sa yaqum al-dhaka' al-istina'i bi inhiraf al-mu'ashshirat.",
        "rhythm_flow": "AL-IQA' & ALTADAFFUQ", "tempo": "Iqa'",
        "chaos": "Fawda", "chaos_tip": "Ihitmaliyyat al-taghayyurat",
        "environment": "ALBI'A",
        "intensity": "Shidda", "intensity_tip": "Kathafa wa hajm",
        "gravity": "Jadhbiyya", "gravity_tip": "Inhiyaz al-nit: Ali vs Munkhafid",
        "strings": "AWTTAR", "winds_brass": "RIYAH & NUHAS", "keys": "MAFATIH",
        "percussion": "IIQAA'IYYAT", "ethereal": "ATHIRI & ASWAT", "mood": "MZAJ",
        "violin": "Kaman", "viola": "Fiula", "cello": "Tshilu", "contrabass": "Kuntrabas",
        "harp": "Qithara", "guitar": "Gitar", "pizzicato": "Bitzikatu", "bass": "Bas",
        "flute": "Nay", "piccolo": "Bikulu", "clarinet": "Klarinat", "oboe": "Ubu",
        "bassoon": "Basun", "trumpet": "Burj", "horn": "Qarn", "brass": "Nuhas",
        "piano": "Bianu", "organ": "Urghun", "harpsichord": "Harbsikurd", "accordion": "Akurdiun",
        "timpani": "Timbal", "drums": "Tubl", "xylophone": "Ksilufun", "glockenspiel": "Glukinshbil",
        "choir": "Jauqa", "voice": "Sawt", "celesta": "Silista", "bells": "Ajras",
        "random_flow": "Tadaffuq 'Ashwa'i", "creative": "Wadh Ibda'i",
        "joy": "Farah", "melancholy": "Huzn", "action": "Haraka",
        "suspense": "Tashwiq", "epic": "Malahimi",
        "earth": "Ard", "water": "Ma'", "fire": "Nar", "air": "Hawa'", "space": "Fada'",
        "winter": "Shita'", "spring": "Rabi'", "summer": "Sayf", "autumn": "Kharif", "void": "Faragh",
        "zen": "Zen", "cyber": "Sibir", "lofi": "LoFi", "thunder": "Ra'd", "traffic": "Murur",
        "quit": "KHURUJ", "quit_tip": "Khuruj min al-Tatbiq", "focus_mode": "Wadh Tarkiz",
        "exit_focus": "KHURUJ TARKIZ", "save_profile": "HIFZ", "saved": "MAHFUZ",
        "profile_name": "Ism al-Milaf", "cancel": "ILGHA'", "save": "HIFZ",
        "mute": "Kitmm/Taf'il", "ambience_vol": "Hajm al-Ajwa'",
        "zen_finished": "Intahat Jalsa Zen", "zen_set": "Muaqqit Zen muddat",
        "off": "Matlaq",
    },
}

def T(key):
    """Get translated string for current language. Falls back to EN then to key itself."""
    lang = SETTINGS.get("language", "EN")
    tr = TRANSLATIONS.get(lang, TRANSLATIONS["EN"])
    return tr.get(key, TRANSLATIONS["EN"].get(key, key))

def load_settings_from_storage(page):
    """Hydrate config.SETTINGS from page.client_storage on startup."""
    for key, default in SETTINGS_DEFAULTS.items():
        try:
            stored = page.client_storage.get(f"quoniam.setting.{key}")
            SETTINGS[key] = stored if stored is not None else default
        except Exception:
            SETTINGS[key] = default

def save_setting(page, key, value):
    """Save a single setting to runtime dict + persistent storage."""
    SETTINGS[key] = value
    try:
        page.client_storage.set(f"quoniam.setting.{key}", value)
    except Exception:
        pass

def reset_all_settings(page):
    """Reset all settings to defaults and clear storage."""
    for key, default in SETTINGS_DEFAULTS.items():
        SETTINGS[key] = default
        try:
            page.client_storage.remove(f"quoniam.setting.{key}")
        except Exception:
            pass
