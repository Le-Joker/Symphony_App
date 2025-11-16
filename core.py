"""Cœur de l'application Symphony - Gestion centralisée de l'audio et des données.

Architecture optimisée et modulaire pour l'application de balafon.
"""

import numpy as np
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    sd = None
    sf = None

from scipy import signal


@dataclass
class Note:
    """Représentation d'une note musicale."""
    name: str
    frequency: float
    octave: int


class AudioCore:
    """Moteur audio centralisé pour la synthèse et l'analyse."""

    # Fréquences de base
    TUNING_A4 = 440.0
    A4_INDEX = 9
    SEMITONE_RATIO = 2 ** (1 / 12)
    CHROMATIC_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self, sample_rate: int = 44100, volume: float = 0.7):
        self.sample_rate = sample_rate
        self.volume = volume
        self.sample_cache: Dict[float, np.ndarray] = {}
        self._lock = threading.Lock()
        self._is_playing = False

    def get_frequency(self, note: str, octave: int = 4) -> float:
        """Calcule la fréquence d'une note."""
        if note not in self.CHROMATIC_NOTES:
            raise ValueError(f"Note inconnue : {note}")
        
        note_index = self.CHROMATIC_NOTES.index(note)
        semitone_distance = (octave - 4) * 12 + (note_index - self.A4_INDEX)
        return self.TUNING_A4 * (self.SEMITONE_RATIO ** semitone_distance)

    def build_balafon_scale(self, style: str = "pentatonic") -> list:
        """Génère 22 notes pour le balafon selon le style."""
        scales = {
            "pentatonic": [0, 2, 4, 7, 9],  # Do, Ré, Mi, Sol, La
            "major": [0, 2, 4, 5, 7, 9, 11],  # Do, Ré, Mi, Fa, Sol, La, Si
            "chromatic": list(range(12)),
        }
        
        pattern = scales.get(style, scales["pentatonic"])
        notes = []
        octave = 4
        
        while len(notes) < 22:
            for semitone in pattern:
                if len(notes) >= 22:
                    break
                note_idx = semitone % 12
                note_name = self.CHROMATIC_NOTES[note_idx]
                notes.append(Note(
                    name=note_name,
                    frequency=self.get_frequency(note_name, octave),
                    octave=octave
                ))
            octave += 1
        
        return notes[:22]

    def generate_sample(
        self,
        frequency: float,
        duration: float = 0.45,
        add_harmonics: bool = True
    ) -> np.ndarray:
        """Génère un sample de note avec harmoniques et enveloppe."""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Onde fondamentale
        wave = np.sin(2 * np.pi * frequency * t)

        # Harmoniques (résonance du bois)
        if add_harmonics:
            wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # Harmonique 2
            wave += 0.15 * np.sin(2 * np.pi * frequency * 3 * t)  # Harmonique 3

        # Enveloppe ADSR percussive
        attack_time = 0.005
        attack_samples = max(1, int(self.sample_rate * attack_time))
        envelope = np.ones(n_samples)
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay exponentiel
        decay_rate = -3 * np.log(0.01) / duration
        envelope[attack_samples:] = np.exp(-decay_rate * t[attack_samples:])

        sample = (wave * envelope * self.volume).astype(np.float32)
        return sample

    def get_cached_sample(self, frequency: float) -> np.ndarray:
        """Récupère ou génère un sample du cache."""
        cache_key = round(frequency, 2)
        
        with self._lock:
            if cache_key not in self.sample_cache:
                self.sample_cache[cache_key] = self.generate_sample(frequency)
            return self.sample_cache[cache_key]

    def clear_cache(self):
        """Vide le cache."""
        with self._lock:
            self.sample_cache.clear()

    def play_async(self, frequency: float):
        """Joue une note de manière asynchrone."""
        if sd is None:
            return

        sample = self.get_cached_sample(frequency)

        def _play():
            try:
                self._is_playing = True
                sd.play(sample, self.sample_rate)
                sd.wait()
                self._is_playing = False
            except Exception as e:
                print(f"Erreur playback: {e}")

        thread = threading.Thread(target=_play, daemon=True)
        thread.start()

    def analyze_spectrum(self, sample: np.ndarray, freq_range: int = 2000) -> Tuple:
        """Analyse le spectre FFT du sample."""
        fft = np.abs(np.fft.rfft(sample))
        freqs = np.fft.rfftfreq(len(sample), 1 / self.sample_rate)
        
        # Limiter à freq_range
        idx = np.where(freqs <= freq_range)[0]
        freqs = freqs[idx]
        fft = fft[idx]
        
        # Normaliser
        if fft.max() > 0:
            fft = fft / fft.max()
        
        return freqs, fft

    def save_recording(self, samples: np.ndarray, filepath: str) -> bool:
        """Sauvegarde un enregistrement."""
        if sf is None:
            return False
        try:
            sf.write(filepath, samples, self.sample_rate)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False

    def load_recording(self, filepath: str) -> Optional[np.ndarray]:
        """Charge un enregistrement."""
        if sf is None:
            return None
        try:
            data, sr = sf.read(filepath, dtype='float32')
            return data
        except Exception as e:
            print(f"Erreur chargement: {e}")
            return None


# Instance globale
audio_core = AudioCore()
