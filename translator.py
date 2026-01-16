from google import genai


# =========================
# Diccionario de idiomas
# =========================
IDIOMAS = {
    "español": "es",
    "catalán": "ca",
    "inglés": "en",
    "francés": "fr",
    "portugués": "pt",
    "italiano": "it",
    "alemán": "de",
    "chino": "zh",
    "japonés": "ja",
}


def traducir_texto(texto: str, idioma_destino: str, api_key: str) -> str:
    """
    Traduce un texto al idioma indicado usando Gemini.

    :param texto: Texto original a traducir
    :param idioma_destino: Idioma en texto ('español', 'catalán', etc.)
    :param api_key: API Key de Gemini
    :return: Texto traducido
    """

    # =========================
    # 1. Validaciones
    # =========================
    if not texto or not texto.strip():
        raise ValueError("❌ El texto a traducir está vacío")

    idioma_destino = idioma_destino.lower()

    if idioma_destino not in IDIOMAS:
        raise ValueError(f"❌ Idioma no soportado: {idioma_destino}")

    # =========================
    # 2. Crear cliente Gemini
    # =========================
    client = genai.Client(api_key=api_key)

    codigo_idioma = IDIOMAS[idioma_destino]

    # =========================
    # 3. Prompt de traducción
    # =========================
    prompt = (
        f"Traduce el siguiente texto al idioma con código '{codigo_idioma}'. "
        f"No añadas explicaciones. Devuelve solo la traducción.\n\n"
        f"{texto}"
    )

    # =========================
    # 4. Llamada a la API
    # =========================
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        raise RuntimeError(f"❌ Error al traducir con Gemini: {e}")
