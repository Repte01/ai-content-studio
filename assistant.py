import base64
import io
from google import genai
from PIL import Image

MAX_IMAGE_SIZE_MB = 5


def describir_imagen(imagen_subida, api_key: str, nivel_detalle: str = "normal") -> str:
    """
    Genera una descripción detallada de una imagen usando Gemini.
    
    :param imagen_subida: Archivo de imagen subido
    :param api_key: API Key de Gemini
    :param nivel_detalle: "breve", "normal", "detallado"
    :return: Descripción de la imagen
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
    # Abrir imagen
    # =========================
    image = Image.open(imagen_subida)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    # =========================
    # Base64
    # =========================
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # =========================
    # Definir prompts según nivel de detalle
    # =========================
    prompts = {
        "breve": (
            "Describe esta imagen brevemente en 2-3 frases. "
            "Menciona solo los elementos más importantes."
        ),
        "normal": (
            "Describe esta imagen de manera clara y completa. "
            "Incluye: escenario principal, elementos visibles, colores, "
            "personas u objetos relevantes, y el contexto general."
        ),
        "detallado": (
            "Describe esta imagen con gran detalle. "
            "Incluye: composición, colores, iluminación, "
            "texturas, objetos específicos, personas (descripción si hay), "
            "expresiones, entorno, atmósfera, y posibles significados o contexto."
        )
    }
    
    prompt = prompts.get(nivel_detalle, prompts["normal"])

    # =========================
    # Cliente Gemini
    # =========================
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
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
    )

    return response.text


def analizar_imagen_avanzado(imagen_subida, api_key: str, tipo_analisis: str = "general") -> str:
    """
    Análisis avanzado de imágenes con diferentes enfoques.
    
    :param imagen_subida: Archivo de imagen subido
    :param api_key: API Key de Gemini
    :param tipo_analisis: "general", "tecnico", "artistico", "emocional"
    :return: Análisis de la imagen
    """
    
    # Validar tamaño (reutilizando código)
    imagen_subida.seek(0, io.SEEK_END)
    size_mb = imagen_subida.tell() / (1024 * 1024)
    imagen_subida.seek(0)

    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(
            f"❌ La imagen pesa {size_mb:.2f} MB. "
            f"El máximo permitido es {MAX_IMAGE_SIZE_MB} MB."
        )

    # Abrir imagen
    image = Image.open(imagen_subida)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Definir prompts según tipo de análisis
    prompts = {
        "general": (
            "Analiza esta imagen completamente. Incluye: "
            "1. Descripción general de la escena\n"
            "2. Elementos principales y secundarios\n"
            "3. Colores y composición\n"
            "4. Posible contexto o significado\n"
            "5. Calidad técnica de la imagen"
        ),
        "tecnico": (
            "Haz un análisis técnico de esta imagen. Incluye: "
            "1. Composición y regla de tercios\n"
            "2. Iluminación y sombras\n"
            "3. Enfoque y profundidad de campo\n"
            "4. Colores y balance de blancos\n"
            "5. Posibles ajustes de cámara usados\n"
            "6. Calidad técnica general"
        ),
        "artistico": (
            "Haz un análisis artístico de esta imagen. Incluye: "
            "1. Estilo artístico\n"
            "2. Uso del color y contraste\n"
            "3. Composición y simetría\n"
            "4. Emociones transmitidas\n"
            "5. Influencias artísticas posibles\n"
            "6. Valor estético general"
        ),
        "emocional": (
            "Analiza el contenido emocional de esta imagen. Incluye: "
            "1. Emociones principales transmitidas\n"
            "2. Elementos que generan esas emociones\n"
            "3. Colores y su impacto emocional\n"
            "4. Composición y su efecto en el espectador\n"
            "5. Mensaje emocional general\n"
            "6. Cómo podría afectar a diferentes personas"
        )
    }
    
    prompt = prompts.get(tipo_analisis, prompts["general"])
    
    # Cliente Gemini
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
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
    )

    return response.text