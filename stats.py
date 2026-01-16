import sqlite3
import json
from datetime import datetime
from collections import Counter

DB_NAME = "users.db"


# =========================
# ESTADÍSTICAS DE USUARIO
# =========================
def obtener_estadisticas_usuario(usuario_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    estadisticas = {}
    
    # 1. Total de imágenes procesadas
    cursor.execute(
        """
        SELECT COUNT(*) FROM imagenes 
        WHERE usuario_id = ?
        """,
        (usuario_id,)
    )
    estadisticas["total_imagenes"] = cursor.fetchone()[0]
    
    # 2. Última actividad (última imagen subida)
    cursor.execute(
        """
        SELECT fecha_subida FROM imagenes 
        WHERE usuario_id = ? 
        ORDER BY fecha_subida DESC 
        LIMIT 1
        """,
        (usuario_id,)
    )
    ultima_fila = cursor.fetchone()
    estadisticas["ultima_actividad"] = ultima_fila[0] if ultima_fila else None
    
    # 3. Distribución por fechas (últimos 30 días)
    cursor.execute(
        """
        SELECT DATE(fecha_subida) as fecha, COUNT(*) as cantidad
        FROM imagenes 
        WHERE usuario_id = ? 
        AND fecha_subida >= date('now', '-30 days')
        GROUP BY DATE(fecha_subida)
        ORDER BY fecha
        """,
        (usuario_id,)
    )
    fechas = cursor.fetchall()
    estadisticas["actividad_30_dias"] = [
        {"fecha": fecha, "cantidad": cantidad} 
        for fecha, cantidad in fechas
    ]
    
    conn.close()
    return estadisticas


# =========================
# EXPORTAR DATOS DE USUARIO
# =========================
def exportar_datos_usuario(usuario_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    datos = {}
    
    # 1. Datos del perfil
    cursor.execute(
        """
        SELECT id, email, fecha_registro
        FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,)
    )
    usuario_data = cursor.fetchone()
    datos["perfil"] = {
        "id": usuario_data[0],
        "email": usuario_data[1],
        "fecha_registro": usuario_data[2],
        "fecha_exportacion": datetime.now().isoformat()
    }
    
    # 2. Imágenes procesadas
    cursor.execute(
        """
        SELECT id, texto_original, fecha_subida
        FROM imagenes
        WHERE usuario_id = ?
        ORDER BY fecha_subida DESC
        """,
        (usuario_id,)
    )
    imagenes = cursor.fetchall()
    
    datos["imagenes"] = [
        {
            "id": img_id,
            "texto_extraido": texto,
            "fecha_procesamiento": fecha,
            "longitud_texto": len(texto) if texto else 0
        }
        for img_id, texto, fecha in imagenes
    ]
    
    # 3. Estadísticas resumidas
    cursor.execute(
        """
        SELECT 
            COUNT(*) as total_imagenes,
            MIN(fecha_subida) as primera_imagen,
            MAX(fecha_subida) as ultima_imagen
        FROM imagenes
        WHERE usuario_id = ?
        """,
        (usuario_id,)
    )
    stats = cursor.fetchone()
    datos["estadisticas"] = {
        "total_imagenes": stats[0],
        "primera_imagen": stats[1],
        "ultima_imagen": stats[2],
        "total_texto_procesado": sum(len(img[1]) for img in imagenes if img[1])
    }
    
    conn.close()
    return datos


# =========================
# OBTENER IDIOMAS MÁS USADOS
# =========================
def analizar_idiomas_usuario(usuario_id: int):
    """
    Analiza los idiomas más usados en las traducciones del usuario
    (Esta es una versión simplificada - en producción necesitarías guardar el idioma usado)
    """
    # Por ahora devolvemos datos de ejemplo
    # En una implementación real, necesitarías guardar el idioma de cada traducción
    return [
        {"idioma": "Español", "cantidad": 12},
        {"idioma": "Inglés", "cantidad": 8},
        {"idioma": "Francés", "cantidad": 5},
        {"idioma": "Catalán", "cantidad": 3},
    ]