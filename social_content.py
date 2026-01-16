import base64
import io
from PIL import Image
from google import genai
import json
import re

MAX_IMAGE_SIZE_MB = 5

def generar_contenido_redes(imagen_subida, api_key: str, estilo: str = "profesional", plataforma: str = "instagram") -> dict:
    """
    Genera contenido para redes sociales a partir de una imagen.
    
    Args:
        imagen_subida: Archivo de imagen
        api_key: API Key de Gemini
        estilo: "profesional", "creativo", "humoristico", "inspirador"
        plataforma: "instagram", "twitter", "linkedin", "tiktok"
    
    Returns:
        Diccionario con contenido generado
    """
    
    # =========================
    # Validar tamaño de imagen
    # =========================
    imagen_subida.seek(0, io.SEEK_END)
    size_mb = imagen_subida.tell() / (1024 * 1024)
    imagen_subida.seek(0)

    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(
            f"❌ La imagen pesa {size_mb:.2f} MB. "
            f"El máximo permitido es {MAX_IMAGE_SIZE_MB} MB."
        )

    # =========================
    # Preparar imagen para Gemini
    # =========================
    image = Image.open(imagen_subida)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # =========================
    # Definir estilos según plataforma
    # =========================
    estilos_descripcion = {
        "profesional": "profesional y formal, adecuado para LinkedIn o comunicados corporativos",
        "creativo": "creativo y visual, perfecto para Instagram o Pinterest",
        "humoristico": "divertido y humorístico, ideal para Twitter o memes",
        "inspirador": "inspirador y motivacional, bueno para Facebook o historias personales"
    }
    
    plataformas_caracteristicas = {
        "instagram": {
            "max_caracteres": 2200,
            "hashtags_recomendados": 5,
            "emoji_frecuentes": True
        },
        "twitter": {
            "max_caracteres": 280,
            "hashtags_recomendados": 3,
            "emoji_frecuentes": True
        },
        "linkedin": {
            "max_caracteres": 3000,
            "hashtags_recomendados": 3,
            "emoji_frecuentes": False
        },
        "tiktok": {
            "max_caracteres": 150,
            "hashtags_recomendados": 5,
            "emoji_frecuentes": True
        }
    }
    
    # Obtener config de plataforma
    config = plataformas_caracteristicas.get(plataforma, plataformas_caracteristicas["instagram"])
    
    # =========================
    # Prompt optimizado para API gratuita
    # =========================
    prompt = f"""
    ANALIZA ESTA IMAGEN Y GENERA CONTENIDO PARA REDES SOCIALES.
    
    REQUISITOS:
    1. Estilo: {estilos_descripcion.get(estilo, "profesional")}
    2. Plataforma: {plataforma.upper()}
    3. Límite caracteres: {config['max_caracteres']}
    4. {config['hashtags_recomendados']} hashtags relevantes
    5. {'Incluye emojis apropiados' if config['emoji_frecuentes'] else 'No uses emojis'}
    
    GENERA UN JSON CON ESTE FORMATO EXACTO:
    {{
        "titulo": "Título atractivo (máx 10 palabras)",
        "descripcion_corta": "Descripción breve de la imagen",
        "contenido_post": "Texto completo para el post",
        "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
        "emoji_recomendados": ["😊", "🌟"],
        "consejos_publicacion": "Consejo breve para mejor engagement",
        "hora_optima": "Mañana/Tarde/Noche según contenido",
        "palabras_clave": ["palabra1", "palabra2", "palabra3"]
    }}
    
    IMPORTANTE: Solo devuelve el JSON, sin texto adicional.
    """
    
    # =========================
    # Llamada a Gemini - USANDO MODELO CORRECTO
    # =========================
    client = genai.Client(api_key=api_key)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",  # Modelo experimental gratuito y rápido
            # O alternativamente usa: "gemini-1.5-flash" (pero en versión correcta)
            contents=[
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64,
                            }
                        },
                        {"text": prompt},
                    ]
                }
            ],
            config={
                "temperature": 0.7,
                "max_output_tokens": 500
            }
        )
        
        # Extraer JSON de la respuesta
        response_text = response.text.strip()
        
        # Limpiar y encontrar JSON
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        try:
            contenido = json.loads(response_text)
            
            # Validar estructura básica
            campos_requeridos = ["titulo", "contenido_post", "hashtags"]
            for campo in campos_requeridos:
                if campo not in contenido:
                    contenido[campo] = ""
            
            return contenido
            
        except json.JSONDecodeError:
            # Si falla el JSON, intentar extraer información manualmente
            return extraer_contenido_manual(response_text, estilo, plataforma)
            
    except Exception as e:
        # Si hay error con el modelo, probar con alternativas
        try:
            return generar_contenido_con_modelo_alternativo(
                image_base64, prompt, api_key, estilo, plataforma
            )
        except:
            # Si todo falla, generar respuesta básica
            return generar_respuesta_fallback(estilo, plataforma)


def extraer_contenido_manual(texto_respuesta: str, estilo: str, plataforma: str) -> dict:
    """Intenta extraer contenido manualmente si el JSON falla"""
    contenido = {
        "titulo": f"Imagen {estilo.capitalize()}",
        "descripcion_corta": f"Contenido generado para {plataforma}",
        "contenido_post": texto_respuesta[:500],
        "hashtags": [f"#{estilo}", f"#{plataforma}", "#IA", "#ContenidoGenerado"],
        "emoji_recomendados": ["✨", "📸", "👁️"],
        "consejos_publicacion": "Publica en horarios de mayor actividad para mejor alcance",
        "hora_optima": "Tarde",
        "palabras_clave": [estilo, plataforma, "contenido", "IA"]
    }
    return contenido


def generar_contenido_con_modelo_alternativo(image_base64: str, prompt: str, api_key: str, estilo: str, plataforma: str) -> dict:
    """Prueba con otros modelos disponibles"""
    client = genai.Client(api_key=api_key)
    
    # Lista de modelos a probar (de más reciente a menos)
    modelos_a_probar = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash-8b",  # Versión de 8B parámetros
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]
    
    for modelo in modelos_a_probar:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=[
                    {
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": image_base64,
                                }
                            },
                            {"text": prompt},
                        ]
                    }
                ],
                config={
                    "temperature": 0.7,
                    "max_output_tokens": 500
                }
            )
            
            response_text = response.text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            contenido = json.loads(response_text)
            
            # Añadir metadatos del modelo usado
            contenido["modelo_usado"] = modelo
            
            return contenido
            
        except:
            continue  # Probar siguiente modelo
    
    # Si todos los modelos fallan
    raise RuntimeError("❌ No se pudo generar contenido con ningún modelo disponible")


def generar_respuesta_fallback(estilo: str, plataforma: str) -> dict:
    """Genera respuesta básica si falla la API"""
    estilos_fallback = {
        "profesional": {
            "titulo": "Imagen Profesional",
            "contenido_post": f"Compartiendo contenido visual relevante para {plataforma}. Una imagen vale más que mil palabras en el entorno digital actual.",
            "hashtags": [f"#{plataforma.capitalize()}", "#Profesional", "#ContenidoVisual"]
        },
        "creativo": {
            "titulo": "¡Inspiración Creativa! 🎨",
            "contenido_post": "Explorando nuevas perspectivas visuales en esta imagen. La creatividad no tiene límites cuando combinamos arte y tecnología.",
            "hashtags": ["#Creatividad", "#ArteDigital", "#Innovación"]
        },
        "humoristico": {
            "titulo": "Momento Divertido 😄",
            "contenido_post": "Algunas imágenes merecen una sonrisa. ¡Espero que esta te alegre el día tanto como a mí al compartirla!",
            "hashtags": ["#Humor", "#Divertido", "#SonrisaDigital"]
        },
        "inspirador": {
            "titulo": "Reflexión del Día ✨",
            "contenido_post": "Cada imagen cuenta una historia y transmite emociones. Esta captura me recordó la importancia de apreciar los pequeños momentos.",
            "hashtags": ["#Inspiración", "#Motivación", "#Reflexión"]
        }
    }
    
    fallback = estilos_fallback.get(estilo, estilos_fallback["profesional"])
    
    return {
        "titulo": fallback["titulo"],
        "descripcion_corta": f"Imagen en estilo {estilo} optimizada para {plataforma}",
        "contenido_post": fallback["contenido_post"],
        "hashtags": fallback["hashtags"],
        "emoji_recomendados": ["✨", "📸", "👁️", "🚀"],
        "consejos_publicacion": f"Para {plataforma}: Publica entre 11:00-13:00 o 19:00-21:00 para máximo engagement",
        "hora_optima": "Tarde",
        "palabras_clave": [estilo, plataforma, "contenido", "redes sociales", "IA"],
        "nota": "Contenido generado automáticamente como fallback"
    }


def generar_variaciones_contenido(contenido_base: dict, num_variaciones: int = 3) -> list:
    """
    Genera variaciones de un contenido para A/B testing
    """
    variaciones = []
    
    if not contenido_base:
        return variaciones
    
    # Variación 1: Con emoji en título
    if num_variaciones >= 1:
        variacion1 = contenido_base.copy()
        variacion1["titulo"] = f"📸 {contenido_base.get('titulo', '')}"
        variacion1["variacion"] = "Versión con emoji destacado"
        variaciones.append(variacion1)
    
    # Variación 2: Con pregunta para engagement
    if num_variaciones >= 2:
        variacion2 = contenido_base.copy()
        contenido_original = contenido_base.get('contenido_post', '')
        variacion2["contenido_post"] = f"{contenido_original}\n\n¿Qué te parece esta imagen? ¡Déjame tu opinión en los comentarios! 👇"
        variacion2["variacion"] = "Versión con pregunta para comentarios"
        variaciones.append(variacion2)
    
    # Variación 3: Más hashtags estratégicos
    if num_variaciones >= 3:
        variacion3 = contenido_base.copy()
        hashtags_originales = contenido_base.get('hashtags', [])
        hashtags_extra = ["#ContenidoGeneradoPorIA", "#InnovaciónDigital", "#TecnologíaCreativa"]
        variacion3["hashtags"] = hashtags_originales + hashtags_extra
        variacion3["variacion"] = "Versión con más hashtags estratégicos"
        variaciones.append(variacion3)
    
    # Variación 4: Versión ultra-breve (si se piden 4)
    if num_variaciones >= 4:
        variacion4 = contenido_base.copy()
        contenido_breve = contenido_base.get('contenido_post', '')[:150]
        if len(contenido_breve) > 100:
            variacion4["contenido_post"] = contenido_breve + "..."
        variacion4["variacion"] = "Versión ultra-breve"
        variaciones.append(variacion4)
    
    return variaciones


# Función adicional para listar modelos disponibles
def listar_modelos_disponibles(api_key: str) -> list:
    """Lista los modelos disponibles en la API"""
    try:
        client = genai.Client(api_key=api_key)
        modelos = client.models.list()
        
        modelos_disponibles = []
        for modelo in modelos:
            if "generate" in modelo.supported_generation_methods:
                modelos_disponibles.append(modelo.name)
        
        return sorted(modelos_disponibles)
    except Exception as e:
        return [f"Error al listar modelos: {str(e)}"]