"""Gestion de la base de données - Simplifiée et optimisée.

Gère les utilisateurs et les enregistrements.
"""

import sqlite3
import hashlib
import os
from pathlib import Path
from typing import Optional


class Database:
    """Gestionnaire de base de données centralisé."""

    def __init__(self, db_path: str = "data/symphony.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        """Établit une connexion à la base."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialise les tables."""
        conn = self.get_connection()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS recordings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                duration REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    def hash_password(self, password: str) -> str:
        """Hache un mot de passe."""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()

    def create_user(self, username: str, password: str) -> bool:
        """Crée un utilisateur."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, self.hash_password(password))
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> Optional[int]:
        """Vérifie un utilisateur. Retourne son ID ou None."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = c.fetchone()
        conn.close()

        if row and row['password_hash'] == self.hash_password(password):
            return row['id']
        return None

    def save_recording(self, user_id: int, filename: str, duration: float):
        """Enregistre une métadonnée d'enregistrement."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO recordings (user_id, filename, duration) VALUES (?, ?, ?)",
            (user_id, filename, duration)
        )
        conn.commit()
        conn.close()

    def get_recordings(self, user_id: int) -> list:
        """Récupère les enregistrements d'un utilisateur."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT * FROM recordings WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = c.fetchall()
        conn.close()
        return rows
