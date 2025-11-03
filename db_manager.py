import os
import sqlite3
import hashlib
import binascii
from datetime import datetime


def create_db(db_path: str):
    # Crée le dossier parent si nécessaire et initialise les tables
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # table des comptes utilisateurs
    c.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TEXT,
        tutorial_shown INTEGER DEFAULT 0
    )
    """)
    # table des enregistrements (métadonnées)
    c.execute("""
    CREATE TABLE IF NOT EXISTS recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        filename TEXT NOT NULL,
        length_seconds REAL,
        created_at TEXT,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    """)
    conn.commit()
    conn.close()


class DBManager:
    """Gestionnaire simple pour effectuer des opérations CRUD sur la DB.

    - connect / close : gérer la connexion SQLite
    - create_user / verify_user / delete_user : gestion des comptes
    - add_recording / list_recordings : gestion des métadonnées des enregistrements
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None

    def connect(self):
        self._conn = sqlite3.connect(self.db_path)
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    @staticmethod
    def _hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
        if salt is None:
            salt = os.urandom(16)
        # PBKDF2 HMAC SHA256
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
        return binascii.hexlify(dk).decode('ascii'), binascii.hexlify(salt).decode('ascii')

    def create_user(self, username: str, password: str) -> bool:
        # Créer un utilisateur avec mot de passe haché (PBKDF2)
        conn = self._conn or sqlite3.connect(self.db_path)
        c = conn.cursor()
        # vérifier si l'utilisateur existe déjà
        c.execute("SELECT id FROM accounts WHERE username = ?", (username,))
        if c.fetchone():
            if self._conn is None:
                conn.close()
            return False
        pwd_hash, salt = self._hash_password(password)
        now = datetime.utcnow().isoformat()
        c.execute("INSERT INTO accounts (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                  (username, pwd_hash, salt, now))
        conn.commit()
        if self._conn is None:
            conn.close()
        return True

    def verify_user(self, username: str, password: str) -> bool:
        # Vérifier les identifiants utilisateur : comparer le hash
        conn = self._conn or sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT password_hash, salt FROM accounts WHERE username = ?", (username,))
        row = c.fetchone()
        if row is None:
            if self._conn is None:
                conn.close()
            return False
        stored_hash, stored_salt = row
        salt = binascii.unhexlify(stored_salt.encode('ascii'))
        computed_hash, _ = self._hash_password(password, salt)
        if self._conn is None:
            conn.close()
        return computed_hash == stored_hash

    def delete_user(self, username: str) -> bool:
        # Supprimer un utilisateur et ses enregistrements (si présents)
        conn = self._conn or sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id FROM accounts WHERE username = ?", (username,))
        row = c.fetchone()
        if row is None:
            if self._conn is None:
                conn.close()
            return False
        user_id = row[0]
        # suppression des enregistrements liés
        c.execute("DELETE FROM recordings WHERE account_id = ?", (user_id,))
        c.execute("DELETE FROM accounts WHERE id = ?", (user_id,))
        conn.commit()
        if self._conn is None:
            conn.close()
        return True

    def list_users(self):
        conn = self._conn or sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, username, created_at FROM accounts")
        rows = c.fetchall()
        if self._conn is None:
            conn.close()
        return rows

    def add_recording(self, account_id: int, filename: str, length_seconds: float):
        conn = self._conn or sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute("INSERT INTO recordings (account_id, filename, length_seconds, created_at) VALUES (?, ?, ?, ?)",
                  (account_id, filename, length_seconds, now))
        conn.commit()
        if self._conn is None:
            conn.close()

    def list_recordings(self, account_id: int = None):
        conn = self._conn or sqlite3.connect(self.db_path)
        c = conn.cursor()
        if account_id is None:
            c.execute("SELECT id, account_id, filename, length_seconds, created_at FROM recordings ORDER BY created_at DESC")
        else:
            c.execute("SELECT id, account_id, filename, length_seconds, created_at FROM recordings WHERE account_id = ? ORDER BY created_at DESC", (account_id,))
        rows = c.fetchall()
        if self._conn is None:
            conn.close()
        return rows

    def get_user_id(self, username: str):
        conn = self._conn or sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id FROM accounts WHERE username = ?", (username,))
        row = c.fetchone()
        if self._conn is None:
            conn.close()
        return row[0] if row else None
