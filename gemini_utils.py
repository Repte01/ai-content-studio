import base64
from google import genai
from PIL import Image
import io

def entender_imagen(imagen_file, api_key: str):
    # convierte la imagen a base64
    image_bytes = imagen_file.read()
    base64_str = base64.b64encode(image_bytes).decode("utf-8")

    # cliente de Gemini
    client = genai.Client(api_key=api_key)

    # petición al modelo con imagen
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{
            "parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_str}},
                {"text": "Describe esta imagen y tradúcela al español"}
            ]
        }],
    )
    return response.text
