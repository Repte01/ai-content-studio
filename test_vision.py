import os
from dotenv import load_dotenv
from utils.gemini_vision import extraer_texto_imagen

# =========================
# 1. Cargar variables .env
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se ha encontrado la variable GEMINI_API_KEY en el .env")

# =========================
# 2. Ruta de imagen local
# =========================
RUTA_IMAGEN = "ejemplo.png"  # cambia el nombre si hace falta

if not os.path.exists(RUTA_IMAGEN):
    raise FileNotFoundError(f"❌ No existe la imagen: {RUTA_IMAGEN}")

# =========================
# 3. Abrir imagen en binario
# =========================
with open(RUTA_IMAGEN, "rb") as imagen:
    print("📸 Imagen cargada correctamente")
    print("🤖 Enviando imagen a Gemini...\n")

    texto = extraer_texto_imagen(imagen, API_KEY)

# =========================
# 4. Mostrar resultado
# =========================
print("✅ TEXTO DETECTADO:")
print("--------------------")
print(texto)
