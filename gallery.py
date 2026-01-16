import sqlite3
from datetime import datetime

DB_NAME = "users.db"


# =========================
# CREAR TABLA IMÁGENES
# =========================
def init_gallery_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            imagen_blob BLOB NOT NULL,
            texto_original TEXT,
            fecha_subida TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================
# GUARDAR IMAGEN
# =========================
def guardar_imagen(usuario_id: int, imagen_bytes: bytes, texto_original: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO imagenes (usuario_id, imagen_blob, texto_original, fecha_subida)
        VALUES (?, ?, ?, ?)
        """,
        (
            usuario_id,
            imagen_bytes,
            texto_original,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


# =========================
# OBTENER IMÁGENES DE USUARIO
# =========================
def obtener_imagenes_usuario(usuario_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, imagen_blob, texto_original, fecha_subida
        FROM imagenes
        WHERE usuario_id = ?
        ORDER BY fecha_subida DESC
        """,
        (usuario_id,)
    )

    filas = cursor.fetchall()
    conn.close()

    return filas


# =========================
# OBTENER UNA IMAGEN POR ID
# =========================
def obtener_imagen_por_id(imagen_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT imagen_blob, texto_original
        FROM imagenes
        WHERE id = ?
        """,
        (imagen_id,)
    )

    fila = cursor.fetchone()
    conn.close()

    return fila


# =========================
# ELIMINAR IMAGEN POR ID
# =========================
def eliminar_imagen(imagen_id: int, usuario_id: int):
    """
    Elimina una imagen específica solo si pertenece al usuario
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verificar que la imagen pertenece al usuario antes de eliminar
    cursor.execute(
        """
        DELETE FROM imagenes 
        WHERE id = ? AND usuario_id = ?
        """,
        (imagen_id, usuario_id)
    )
    
    eliminadas = cursor.rowcount
    conn.commit()
    conn.close()
    
    return eliminadas > 0


# =========================
# ELIMINAR VARIAS IMÁGENES
# =========================
def eliminar_imagenes(imagenes_ids: list, usuario_id: int):
    """
    Elimina múltiples imágenes que pertenezcan al usuario
    """
    if not imagenes_ids:
        return 0
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Crear placeholders para la consulta SQL
    placeholders = ','.join(['?'] * len(imagenes_ids))
    
    cursor.execute(
        f"""
        DELETE FROM imagenes 
        WHERE id IN ({placeholders}) AND usuario_id = ?
        """,
        (*imagenes_ids, usuario_id)
    )
    
    eliminadas = cursor.rowcount
    conn.commit()
    conn.close()
    
    return eliminadas