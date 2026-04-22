import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "users.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS emotion_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            emotion TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, email: str, password: str) -> dict:
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username.strip(), email.strip().lower(), hash_password(password), datetime.now().isoformat())
        )
        conn.commit()
        return {"success": True, "message": "Account created successfully!"}
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return {"success": False, "message": "Username already taken."}
        return {"success": False, "message": "Email already registered."}
    finally:
        conn.close()

def login_user(username: str, password: str) -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username.strip(), hash_password(password))
    )
    user = c.fetchone()
    if user:
        c.execute("UPDATE users SET last_login = ? WHERE id = ?",
                  (datetime.now().isoformat(), user["id"]))
        conn.commit()
        conn.close()
        return {"success": True, "user": dict(user)}
    conn.close()
    return {"success": False, "message": "Invalid username or password."}

def save_chat_message(user_id: int, role: str, content: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, role, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id: int) -> list:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_emotion(user_id: int, emotion: str, confidence: float):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO emotion_logs (user_id, emotion, confidence, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, emotion, confidence, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_emotion_history(user_id: int) -> list:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT emotion, confidence, timestamp FROM emotion_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize DB on import
init_db()