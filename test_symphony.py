"""Tests d'intégration pour Symphony - Application de Balafon.

Valide l'ensemble du système : audio, UI, base de données.
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path

from core import audio_core, AudioCore, Note
from database import Database


class TestAudioCore:
    """Tests du moteur audio."""

    def test_get_frequency(self):
        """Teste le calcul des fréquences."""
        # La4 = 440 Hz
        assert abs(audio_core.get_frequency("A", 4) - 440.0) < 1.0

    def test_build_balafon_scale(self):
        """Teste la génération d'échelles."""
        pentatonic = audio_core.build_balafon_scale("pentatonic")
        assert len(pentatonic) == 22
        assert all(isinstance(n, Note) for n in pentatonic)

    def test_generate_sample(self):
        """Teste la génération de samples."""
        sample = audio_core.generate_sample(440.0, duration=0.1)
        assert len(sample) > 0
        assert sample.dtype == np.float32

    def test_cache(self):
        """Teste le cache de samples."""
        audio_core.clear_cache()
        
        sample1 = audio_core.get_cached_sample(440.0)
        sample2 = audio_core.get_cached_sample(440.0)
        
        assert np.array_equal(sample1, sample2)
        audio_core.clear_cache()

    def test_analyze_spectrum(self):
        """Teste l'analyse spectrale."""
        sample = audio_core.generate_sample(440.0)
        freqs, mags = audio_core.analyze_spectrum(sample)
        
        assert len(freqs) > 0
        assert len(mags) > 0
        assert mags.max() <= 1.0


class TestDatabase:
    """Tests de la base de données."""

    @pytest.fixture
    def temp_db(self):
        """Crée une BD temporaire."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = Database(db_path)
            yield db
            # Fermer toute connexion ouverte à la DB
            import gc
            gc.collect()

    def test_create_user(self, temp_db):
        """Teste la création d'utilisateur."""
        assert temp_db.create_user("testuser", "password123")
        assert not temp_db.create_user("testuser", "password123")

    def test_verify_user(self, temp_db):
        """Teste la vérification d'utilisateur."""
        temp_db.create_user("testuser", "password123")
        user_id = temp_db.verify_user("testuser", "password123")
        assert user_id is not None
        assert temp_db.verify_user("testuser", "wrongpass") is None

    def test_save_recording(self, temp_db):
        """Teste la sauvegarde de métadonnées."""
        user_id = temp_db.create_user("testuser", "pass") and 1
        temp_db.save_recording(user_id, "rec.wav", 5.0)
        
        recs = temp_db.get_recordings(user_id)
        assert len(recs) > 0


class TestIntegration:
    """Tests d'intégration complets."""

    def test_audio_to_file(self):
        """Teste la génération et sauvegarde audio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.wav")
            
            sample = audio_core.generate_sample(440.0, duration=0.5)
            success = audio_core.save_recording(sample, filepath)
            
            assert success
            assert os.path.exists(filepath)

    def test_balafon_workflow(self):
        """Teste le workflow complet du balafon."""
        # Générer des notes
        notes = audio_core.build_balafon_scale("pentatonic")
        assert len(notes) == 22
        
        # Générer des samples
        samples = [audio_core.generate_sample(n.frequency) for n in notes[:5]]
        assert all(len(s) > 0 for s in samples)
        
        # Concaténer
        recording = np.concatenate(samples)
        assert len(recording) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
