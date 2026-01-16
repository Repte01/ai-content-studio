import base64
import io
from google import genai
from PIL import Image

MAX_IMAGE_SIZE_MB = 5


def extraer_texto_imagen(imagen_subida, api_key: str) -> str:
    """
    Extrae TODO el texto de una imagen usando Gemini Vision.
    Valida tamaño máximo y formato.
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
    # Cliente Gemini
    # =========================
    client = genai.Client(api_key=api_key)

    prompt = (
        "Extrae TODO el texto que aparezca en esta imagen. "
        "No lo resumas. No lo interpretes. "
        "Devuelve únicamente el texto."
    )

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
