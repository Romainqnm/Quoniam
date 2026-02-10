# QUONIAM v15.0 - Notes de Version

## 🎵 "Nappes Fluides" - Refactoring Audio Majeur

### Changements Architecturaux

#### 1. Séparation UI / Logique Audio

**Avant (v14.x)** :
- `interface.py` (1600+ lignes) : UI Flet + gestion audio mélangées
- `main.py` : Moteur SCAMP importé comme thread
- Couplage fort entre UI et audio

**Après (v15.0)** :
- `interface.py` : Interface Flet uniquement
- `audio_engine.py` : **NOUVEAU** - Classe `QuoniamAudioEngine` dédiée
- `main.py` : Conservé pour compatibilité (peut être supprimé)
- Séparation claire des responsabilités

#### 2. Nouvelle Classe `QuoniamAudioEngine`

**Localisation** : `/audio_engine.py`

**API Publique** :
```python
from audio_engine import QuoniamAudioEngine

# Initialisation
engine = QuoniamAudioEngine(soundfont_path="FluidR3_GM.sf2")

# Contrôle
engine.start()          # Démarre les threads audio
engine.stop()           # Arrête la génération
engine.set_volume(60)   # Ajuste le volume (0-100)
engine.set_mood('zen')  # Change le mood actif
```

**Threading Intégré** :
- Le moteur tourne dans 2 threads séparés :
  - Thread 1 : Nappe harmonique de fond
  - Thread 2 : Génération mélodique principale
- **Non-bloquant** pour l'interface graphique

### Corrections Audio : Nappes Fluides

#### Problème Résolu
❌ **Avant** : Notes saccadées, coupures abruptes, sons "robotiques"
✅ **Après** : Nappes fluides continues, transitions douces

#### Implémentation Technique

##### 1. Enveloppes Dynamiques (`Envelope`)
```python
# Avant (v14.x) - Volume constant
inst.play_note(pitch, volume, duration)

# Après (v15.0) - Envelope fluide
envelope = Envelope.from_levels(
    [0.0, vol, vol * 0.8, 0.0],        # Fade In -> Sustain -> Fade Out
    [0.3, duration * 0.6, duration * 0.4],  # Phases temporelles
    curve_shapes=[2, 0, -2]             # Courbes expressives
)
inst.play_note(pitch, envelope, duration)
```

**Résultat** : Attaque douce (fade-in), sustain expressif, extinction progressive (fade-out)

##### 2. Parallélisation avec `fork()`
```python
# Avant (v14.x) - Séquentiel
for note in accord:
    inst.play_note(note, vol, duration, blocking=True)

# Après (v15.0) - Parallèle
for note in accord:
    session.fork(inst.play_note, note, envelope, duration, blocking=False)
```

**Résultat** : Les notes d'un accord sonnent simultanément (harmonies naturelles)

##### 3. Tuilage Temporel (Overlap)
```python
# Avant (v14.x) - Notes séparées
duration = 2.0
play_note(...)
wait(duration)  # Attente complète = silence entre notes

# Après (v15.0) - Tuilage 50%
duration = random.uniform(3.0, 6.0)  # Durées prolongées
play_note(...)
wait(duration * 0.5)  # Attente partielle = chevauchement !
```

**Résultat** : Les notes se chevauchent, créant une continuité sonore sans blancs

### Compatibilité

#### Fichiers Modifiés
- ✅ `interface.py` : Nettoyé (suppression import `main`)
- ✅ `audio_engine.py` : **CRÉÉ**
- ✅ `requirements.txt` : **CRÉÉ**

#### Fichiers Inchangés
- ✅ `config.py` : État global conservé
- ✅ `gammes.py` : Données musicales conservées
- ✅ `assets_library.py` : Assets graphiques conservés
- ✅ `main.py` : Conservé pour compatibilité (obsolète)

#### Migration
**Aucune action requise** si vous utilisez le point d'entrée standard :
```bash
python interface.py
```

Le nouveau moteur audio est automatiquement utilisé.

### Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python interface.py
```

### Améliorations Futures Possibles

1. **Contrôle Granulaire** : API pour ajuster les paramètres d'envelope en direct
2. **Présets Audio** : Sauvegarder/charger des configurations d'enveloppes
3. **Visualisation** : Afficher les enveloppes en temps réel dans l'UI
4. **Performance** : Pooling de threads pour optimiser les appels `fork()`

---

## Crédits

**Refactoring v15.0** : Séparation UI/Audio + Nappes Fluides
**Architecture** : Classe `QuoniamAudioEngine` avec threading intégré
**Audio Engine** : SCAMP (Simple Composition and Music Performance)
