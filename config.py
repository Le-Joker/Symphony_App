"""Configuration et constantes de l'application Symphony.

Fichier unique regroupant tous les paramétrages.
"""

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

SAMPLE_RATE = 44100
VOLUME = 0.7
DURATION_DEFAULT = 0.45

# Harmoniques pour la synthèse
HARMONICS = {
    2: 0.3,   # 2e harmonique à 30% amplitude
    3: 0.15,  # 3e harmonique à 15% amplitude
}

# ADSR Envelope
ATTACK_TIME = 0.005
DECAY_RATE = -3 * __import__('numpy').log(0.01)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DB_PATH = "data/symphony.db"
DB_CHECK_INTERVAL = 5  # secondes

# ============================================================================
# UI CONFIGURATION
# ============================================================================

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# Thèmes de couleur
THEMES = {
    "dark": {
        "bg": "#0f1419",
        "surface": "#1a1f2e",
        "surface_light": "#242b3d",
        "text": "#f1f5f9",
        "text_muted": "#94a3b8",
        "accent": "#6366f1",
        "accent_light": "#818cf8",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "border": "#334155",
    },
    "light": {
        "bg": "#f8fafc",
        "surface": "#ffffff",
        "surface_light": "#f1f5f9",
        "text": "#1e293b",
        "text_muted": "#64748b",
        "accent": "#6366f1",
        "accent_light": "#818cf8",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "border": "#e2e8f0",
    }
}

DEFAULT_THEME = "dark"

# ============================================================================
# BALAFON CONFIGURATION
# ============================================================================

NUM_NOTES = 22
BASE_NOTE = "C"
BASE_OCTAVE = 4

# Modes d'échelle
SCALES = {
    "pentatonic": [0, 2, 4, 7, 9],      # Do, Ré, Mi, Sol, La
    "major": [0, 2, 4, 5, 7, 9, 11],    # Gamme majeure
    "chromatic": list(range(12)),        # Tous les demi-tons
}

DEFAULT_SCALE = "pentatonic"

# Dimensions des lames (en pixels)
KEY_HEIGHT = 180
KEY_MIN_WIDTH = 30
KEY_MAX_WIDTH = 50

# Mapping clavier AZERTY
KEYBOARD_MAP = {
    'A': 0, 'Z': 1, 'E': 2, 'R': 3, 'T': 4, 'Y': 5, 'U': 6, 'I': 7, 'O': 8, 'P': 9,
    'Q': 10, 'S': 11, 'D': 12, 'F': 13, 'G': 14, 'H': 15, 'J': 16, 'K': 17, 'L': 18,
    'M': 19, 'W': 20, 'X': 21,
}

# ============================================================================
# VISUALIZER CONFIGURATION
# ============================================================================

SPECTRUM_RANGE = 2000  # Hz
OSCILLOSCOPE_SAMPLES = 1000
GRID_ALPHA = 0.3

# ============================================================================
# FILE PATHS
# ============================================================================

RECORDINGS_DIR = "recordings"
DATA_DIR = "data"

# ============================================================================
# SECURITY
# ============================================================================

PASSWORD_HASH_ITERATIONS = 100000
PASSWORD_HASH_ALGORITHM = 'sha256'

# ============================================================================
# PERFORMANCE
# ============================================================================

CACHE_SIZE = 22  # Nombre max de samples en cache
THREAD_DAEMON = True
ANIMATION_DURATION = 150  # ms
