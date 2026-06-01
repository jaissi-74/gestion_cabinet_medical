import hashlib
import sqlite3
import os

DB_PATH = "contacts.db"


def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def create_admin(username, password, db_path=DB_PATH):
    """Creates a new admin account in the database."""
    pw_hash = hash_password(password)
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?,?)",
                (username, pw_hash)
            )
            conn.commit()
        return True, "Admin account created."
    except sqlite3.IntegrityError:
        return False, "Username already exists."


def verify_admin(username, password, db_path=DB_PATH):
    """Returns True if the username/password match a record in the database."""
    pw_hash = hash_password(password)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM admins WHERE username=? AND password_hash=?",
            (username, pw_hash)
        ).fetchone()
    return row is not None


def seed_default_admin(db_path=DB_PATH):
    """Creates a default admin if none exist yet."""
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
    if count == 0:
        create_admin("admin", "admin123", db_path)
