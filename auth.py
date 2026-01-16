import sqlite3
import bcrypt
import re
import json
from datetime import datetime

# En auth.py y gallery.py, cambia:
DB_NAME = "users.db"

# Por algo como:
import tempfile
import os

# Usar directorio temporal en Streamlit Cloud
if "STREAMLIT_CLOUD" in os.environ:
    DB_PATH = os.path.join(tempfile.gettempdir(), "users.db")
else:
    DB_PATH = "users.db"

# =========================
# DB INIT
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# VALIDACIONES
# =========================
def email_valido(email: str) -> bool:
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, email) is not None


def password_segura(password: str) -> bool:
    return len(password) >= 6


# =========================
# REGISTRO
# =========================
def registrar_usuario(email: str, password: str):
    if not email_valido(email):
        raise ValueError("❌ Email no válido")

    if not password_segura(password):
        raise ValueError("❌ La contraseña debe tener al menos 6 caracteres")

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO usuarios (email, password_hash, fecha_registro)
            VALUES (?, ?, ?)
            """,
            (email, password_hash, datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("❌ El email ya está registrado")
    finally:
        conn.close()


# =========================
# LOGIN
# =========================
def login_usuario(email: str, password: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, password_hash FROM usuarios WHERE email = ?
        """,
        (email,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    usuario_id, password_hash = row
    password_hash = password_hash.encode("utf-8")
    
    if bcrypt.checkpw(password.encode("utf-8"), password_hash):
        return usuario_id
    
    return None


# =========================
# OBTENER DATOS DE USUARIO
# =========================
def obtener_datos_usuario(usuario_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, email, fecha_registro
        FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "email": row[1],
            "fecha_registro": row[2]
        }
    return None


# =========================
# CAMBIAR CONTRASEÑA
# =========================
def cambiar_contraseña(usuario_id: int, password_actual: str, nueva_password: str) -> bool:
    if not password_segura(nueva_password):
        raise ValueError("❌ La nueva contraseña debe tener al menos 6 caracteres")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar contraseña actual
    cursor.execute(
        "SELECT password_hash FROM usuarios WHERE id = ?",
        (usuario_id,)
    )
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False

    password_hash_actual = row[0].encode("utf-8")
    
    if not bcrypt.checkpw(password_actual.encode("utf-8"), password_hash_actual):
        conn.close()
        raise ValueError("❌ Contraseña actual incorrecta")

    # Generar nuevo hash
    nuevo_password_hash = bcrypt.hashpw(
        nueva_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # Actualizar en la base de datos
    cursor.execute(
        "UPDATE usuarios SET password_hash = ? WHERE id = ?",
        (nuevo_password_hash, usuario_id)
    )
    
    conn.commit()
    conn.close()

    return True
