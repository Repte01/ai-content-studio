import streamlit as st
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv

import streamlit as st
import os
from dotenv import load_dotenv

import tempfile
import shutil

# Para procesar imágenes
with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
    tmp_file.write(imagen.getvalue())
    tmp_path = tmp_file.name
    
# Procesar imagen...
# Al finalizar:
os.unlink(tmp_path)

# Cargar variables de entorno
load_dotenv()

# Obtener API Key - PRIORIDAD: Streamlit Secrets > .env
API_KEY = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ No se encontró la API Key de Gemini. Configúrala en Streamlit Cloud Secrets.")
    st.stop()

from utils.auth import (
    init_db, 
    registrar_usuario, 
    login_usuario, 
    obtener_datos_usuario,
    cambiar_contraseña
)
from utils.gemini_vision import extraer_texto_imagen
from utils.translator import traducir_texto, IDIOMAS
from utils.gallery import (
    init_gallery_db,
    guardar_imagen,
    obtener_imagenes_usuario,
    eliminar_imagen,
    eliminar_imagenes
)
from utils.stats import (
    obtener_estadisticas_usuario,
    exportar_datos_usuario,
    analizar_idiomas_usuario
)
from utils.assistant import (
    describir_imagen,
    analizar_imagen_avanzado
)
from utils.social_content import (
    generar_contenido_redes,
    generar_variaciones_contenido
)

# =========================
# CONFIGURACIÓN GENERAL
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="OCR y Traducción con Gemini",
    page_icon="🧠",
    layout="wide"
)

# =========================
# INICIALIZAR BASES DE DATOS
# =========================
init_db()
init_gallery_db()

# =========================
# SESSION STATE
# =========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

if "texto_extraido" not in st.session_state:
    st.session_state.texto_extraido = ""

if "texto_traducido" not in st.session_state:
    st.session_state.texto_traducido = ""

if "descripcion_imagen" not in st.session_state:
    st.session_state.descripcion_imagen = ""

if "analisis_avanzado" not in st.session_state:
    st.session_state.analisis_avanzado = ""

# Añadir estado para contenido de redes sociales
if "contenido_redes" not in st.session_state:
    st.session_state.contenido_redes = {}

if "variaciones_contenido" not in st.session_state:
    st.session_state.variaciones_contenido = []

# Añadir estado para selección de imágenes a eliminar
if "imagenes_seleccionadas" not in st.session_state:
    st.session_state.imagenes_seleccionadas = set()

# =========================
# LOGIN / REGISTRO
# =========================
if not st.session_state.autenticado:
    st.title("🔐 Acceso a la aplicación")

    opcion = st.radio("Selecciona una opción", ["Login", "Registro"])
    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Contraseña", type="password")

    if opcion == "Registro":
        if st.button("📝 Registrarse"):
            try:
                registrar_usuario(email, password)
                st.success("✅ Usuario registrado. Ahora inicia sesión.")
            except Exception as e:
                st.error(str(e))

    else:
        if st.button("➡️ Iniciar sesión"):
            usuario_id = login_usuario(email, password)
            if usuario_id:
                st.session_state.autenticado = True
                st.session_state.usuario = email
                st.session_state.usuario_id = usuario_id
                st.rerun()
            else:
                st.error("❌ Email o contraseña incorrectos")

    st.stop()

# =========================
# HEADER PRINCIPAL
# =========================
st.title("🤖 AI Content Studio")
st.caption(f"Usuario: {st.session_state.usuario} | Plataforma todo-en-uno para creación de contenido con IA")

if st.button("🚪 Cerrar sesión"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.divider()

# =========================
# TABS
# =========================
tab_ocr, tab_galeria, tab_perfil, tab_asistente, tab_social = st.tabs([
    "📄 OCR y Traducción", 
    "🖼️ Galería", 
    "👤 Mi Perfil",
    "🤖 Asistente IA",
    "📱 Generador de Contenido"
])

# ======================================================
# TAB OCR Y TRADUCCIÓN
# ======================================================
with tab_ocr:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 Subir imagen para OCR")
        imagen = st.file_uploader(
            "Selecciona una imagen",
            type=["png", "jpg", "jpeg"],
            key="ocr_uploader"
        )

        idioma = st.selectbox(
            "🌍 Idioma de traducción",
            list(IDIOMAS.keys()),
            key="idioma_traduccion"
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            analizar = st.button("🔍 Extraer texto", use_container_width=True)
        with col_btn2:
            traducir = st.button("🌍 Traducir", use_container_width=True)

    with col2:
        if imagen:
            st.image(imagen, use_container_width=True, caption="Vista previa de la imagen")

    # ---------- OCR ----------
    if analizar and imagen:
        with st.spinner("🤖 Extrayendo texto de la imagen..."):
            texto = extraer_texto_imagen(imagen, API_KEY)
            st.session_state.texto_extraido = texto
            st.session_state.texto_traducido = ""

            guardar_imagen(
                usuario_id=st.session_state.usuario_id,
                imagen_bytes=imagen.getvalue(),
                texto_original=texto
            )

        st.success("✅ Texto extraído y guardado en la galería")

    # ---------- TEXTO EXTRAÍDO CON BOTÓN DE COPIAR ----------
    if st.session_state.texto_extraido:
        st.subheader("📄 Texto extraído")
        
        col_texto, col_botones = st.columns([4, 1])
        
        with col_texto:
            texto_area = st.text_area(
                "Texto original",
                st.session_state.texto_extraido,
                height=220,
                key="texto_original_area",
                label_visibility="collapsed"
            )
        
        with col_botones:
            if st.button("📋 Copiar", key="copiar_original", use_container_width=True):
                st.write(f"""<script>
                    navigator.clipboard.writeText(`{st.session_state.texto_extraido.replace('`', '\\`')}`);
                </script>""", unsafe_allow_html=True)
                st.toast("✅ Texto copiado al portapapeles", icon="📋")
            
            palabras = len(st.session_state.texto_extraido.split())
            st.metric("Palabras", palabras)

    # ---------- TRADUCCIÓN ----------
    if traducir and st.session_state.texto_extraido:
        with st.spinner("🌍 Traduciendo..."):
            st.session_state.texto_traducido = traducir_texto(
                st.session_state.texto_extraido,
                idioma,
                API_KEY
            )

    if st.session_state.texto_traducido:
        st.subheader(f"🌐 Texto traducido ({idioma})")
        
        col_texto_trad, col_botones_trad = st.columns([4, 1])
        
        with col_texto_trad:
            texto_trad_area = st.text_area(
                "Traducción",
                st.session_state.texto_traducido,
                height=220,
                key="texto_traducido_area",
                label_visibility="collapsed"
            )
        
        with col_botones_trad:
            if st.button("📋 Copiar", key="copiar_traducido", use_container_width=True):
                st.write(f"""<script>
                    navigator.clipboard.writeText(`{st.session_state.texto_traducido.replace('`', '\\`')}`);
                </script>""", unsafe_allow_html=True)
                st.toast("✅ Traducción copiada al portapapeles", icon="📋")
            
            palabras_trad = len(st.session_state.texto_traducido.split())
            st.metric("Palabras", palabras_trad)

# ======================================================
# TAB GENERADOR DE CONTENIDO (NUEVA)
# ======================================================
with tab_social:
    st.title("📱 Generador de Contenido para Redes Sociales")
    st.markdown("Sube una imagen y genera contenido listo para publicar en diferentes plataformas.")
    
    # Layout principal
    col_config, col_preview = st.columns([2, 3])
    
    with col_config:
        st.subheader("⚙️ Configuración del Contenido")
        
        # Subir imagen
        imagen_social = st.file_uploader(
            "📤 Sube tu imagen",
            type=["png", "jpg", "jpeg"],
            key="social_uploader",
            help="La imagen será analizada para generar contenido relevante"
        )
        
        # Selector de plataforma
        plataforma = st.selectbox(
            "📱 Plataforma de destino",
            ["instagram", "twitter", "linkedin", "tiktok", "facebook"],
            help="El contenido se adaptará a las características de cada plataforma"
        )
        
        # Selector de estilo
        estilo = st.radio(
            "🎨 Estilo del contenido",
            ["profesional", "creativo", "humoristico", "inspirador"],
            horizontal=True,
            help="Selecciona el tono del contenido"
        )
        
        # Opciones avanzadas
        with st.expander("⚡ Opciones avanzadas"):
            generar_variaciones = st.checkbox(
                "Generar variaciones para A/B testing",
                value=True,
                help="Crea diferentes versiones del mismo contenido"
            )
            
            incluir_analisis = st.checkbox(
                "Incluir análisis de engagement",
                value=True,
                help="Añade recomendaciones para mejorar el alcance"
            )
        
        # Botón de generación
        col_generate, col_clear = st.columns(2)
        with col_generate:
            btn_generar = st.button(
                "✨ Generar Contenido", 
                type="primary", 
                use_container_width=True,
                disabled=not imagen_social
            )
        
        with col_clear:
            if st.button("🧹 Limpiar", use_container_width=True):
                st.session_state.contenido_redes = {}
                st.session_state.variaciones_contenido = []
                st.rerun()
    
    with col_preview:
        if imagen_social:
            st.subheader("👁️ Vista previa de la imagen")
            st.image(imagen_social, use_container_width=True, caption="Imagen para contenido social")
            
            # Estadísticas de la imagen
            imagen_social.seek(0, 2)
            tamaño_bytes = imagen_social.tell()
            imagen_social.seek(0)
            
            st.caption(f"📊 Tamaño: {tamaño_bytes / 1024:.1f} KB | 📱 Plataforma: {plataforma.upper()} | 🎨 Estilo: {estilo.capitalize()}")
        
        # Mostrar contenido generado
        if st.session_state.contenido_redes:
            st.subheader("📝 Contenido Generado")
            contenido = st.session_state.contenido_redes
            
            # Tarjeta de contenido principal
            with st.container(border=True):
                col_header, col_copy = st.columns([3, 1])
                with col_header:
                    st.markdown(f"### {contenido.get('titulo', 'Sin título')}")
                with col_copy:
                    if st.button("📋 Copiar todo", key="copiar_todo_social", use_container_width=True):
                        texto_completo = f"{contenido.get('titulo', '')}\n\n{contenido.get('contenido_post', '')}\n\n{' '.join(contenido.get('hashtags', []))}"
                        st.write(f"""<script>
                            navigator.clipboard.writeText(`{texto_completo.replace('`', '\\`')}`);
                        </script>""", unsafe_allow_html=True)
                        st.toast("✅ Contenido copiado", icon="📋")
                
                # Contenido del post
                st.markdown("**📄 Texto del post:**")
                st.info(contenido.get('contenido_post', ''))
                
                # Hashtags
                st.markdown("**🏷️ Hashtags recomendados:**")
                hashtags = contenido.get('hashtags', [])
                hashtags_text = " ".join(hashtags)
                st.code(hashtags_text, language="markdown")
                
                # Emojis recomendados
                emojis = contenido.get('emoji_recomendados', [])
                if emojis:
                    st.markdown(f"**😊 Emojis recomendados:** {' '.join(emojis)}")
                
                # Consejos
                consejos = contenido.get('consejos_publicacion', '')
                if consejos:
                    with st.expander("💡 Consejos de publicación"):
                        st.markdown(consejos)
                
                # Estadísticas
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    caracteres = len(contenido.get('contenido_post', ''))
                    st.metric("Caracteres", caracteres)
                with col_stats2:
                    palabras = len(contenido.get('contenido_post', '').split())
                    st.metric("Palabras", palabras)
                with col_stats3:
                    st.metric("Hashtags", len(hashtags))
    
    # ========== GENERAR CONTENIDO ==========
    if btn_generar and imagen_social:
        with st.spinner("🤖 Generando contenido optimizado..."):
            try:
                contenido = generar_contenido_redes(
                    imagen_social,
                    API_KEY,
                    estilo,
                    plataforma
                )
                st.session_state.contenido_redes = contenido
                
                # Generar variaciones si está activado
                if generar_variaciones:
                    st.session_state.variaciones_contenido = generar_variaciones_contenido(contenido)
                
                # Guardar en galería
                imagen_social.seek(0)
                guardar_imagen(
                    usuario_id=st.session_state.usuario_id,
                    imagen_bytes=imagen_social.getvalue(),
                    texto_original=f"CONTENIDO SOCIAL ({plataforma} - {estilo}):\n{json.dumps(contenido, indent=2)}"
                )
                
                st.success("✅ Contenido generado y guardado en galería")
                
            except Exception as e:
                st.error(f"❌ Error al generar contenido: {str(e)}")
    
    # ========== MOSTRAR VARIACIONES ==========
    if st.session_state.variaciones_contenido and generar_variaciones:
        st.subheader("🔄 Variaciones para A/B Testing")
        
        tabs_variaciones = st.tabs([f"Versión {i+1}" for i in range(len(st.session_state.variaciones_contenido))])
        
        for idx, (tab, variacion) in enumerate(zip(tabs_variaciones, st.session_state.variaciones_contenido)):
            with tab:
                with st.container(border=True):
                    st.markdown(f"**{variacion.get('variacion', f'Versión {idx+1}')}**")
                    
                    col_var1, col_var2 = st.columns([4, 1])
                    with col_var1:
                        st.markdown(variacion.get('contenido_post', ''))
                    with col_var2:
                        if st.button("📋 Copiar", key=f"copiar_var_{idx}", use_container_width=True):
                            texto_var = f"{variacion.get('contenido_post', '')}\n\n{' '.join(variacion.get('hashtags', []))}"
                            st.write(f"""<script>
                                navigator.clipboard.writeText(`{texto_var.replace('`', '\\`')}`);
                            </script>""", unsafe_allow_html=True)
                            st.toast(f"✅ Versión {idx+1} copiada", icon="📋")
                    
                    st.caption(f"Hashtags: {' '.join(variacion.get('hashtags', []))}")
    
    # ========== GUÍA DE USO ==========
    with st.expander("📚 Guía rápida de uso"):
        st.markdown("""
        ### 🎯 Cómo usar el Generador de Contenido:
        
        1. **Sube una imagen** relevante para tu contenido
        2. **Selecciona la plataforma** donde lo publicarás
        3. **Elige el estilo** que mejor se adapte a tu audiencia
        4. **Genera el contenido** y personalízalo si es necesario
        5. **Copia y publica** en tu red social favorita
        
        ### 💡 Consejos por plataforma:
        
        **Instagram:**
        - Usa imágenes de alta calidad
        - Incluye 5-10 hashtags relevantes
        - Publica entre 11:00-13:00 o 19:00-21:00
        
        **Twitter:**
        - Mantén el texto breve (máx 280 caracteres)
        - Usa 1-3 hashtags principales
        - Incluye preguntas para fomentar interacción
        
        **LinkedIn:**
        - Mantén un tono profesional
        - Comparte aprendizajes o insights
        - Usa 3-5 hashtags de industria
        
        **TikTok:**
        - Sé creativo y auténtico
        - Usa tendencias actuales
        - Publica contenido vertical
        """)

# ======================================================
# TAB GALERÍA (sin cambios)
# ======================================================
with tab_galeria:
    st.subheader("🖼️ Mis imágenes guardadas")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Modo Eliminación", type="primary", use_container_width=True):
            st.session_state.imagenes_seleccionadas = set()
            st.rerun()
    
    if st.session_state.imagenes_seleccionadas:
        with st.container():
            st.warning(f"⚠️ {len(st.session_state.imagenes_seleccionadas)} imagen(es) seleccionada(s)")
            col_del1, col_del2, col_del3 = st.columns([1, 1, 2])
            with col_del1:
                if st.button("✅ Eliminar seleccionadas", type="primary", use_container_width=True):
                    try:
                        eliminadas = eliminar_imagenes(
                            list(st.session_state.imagenes_seleccionadas),
                            st.session_state.usuario_id
                        )
                        st.success(f"✅ {eliminadas} imagen(es) eliminada(s)")
                        st.session_state.imagenes_seleccionadas = set()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar: {str(e)}")
            
            with col_del2:
                if st.button("❌ Cancelar selección", use_container_width=True):
                    st.session_state.imagenes_seleccionadas = set()
                    st.rerun()

    imagenes = obtener_imagenes_usuario(st.session_state.usuario_id)

    if not imagenes:
        st.info("Aún no has guardado ninguna imagen")
    else:
        cols = st.columns(3)

        for i, (img_id, img_blob, texto, fecha) in enumerate(imagenes):
            with cols[i % 3]:
                with st.container():
                    st.image(img_blob, use_container_width=True)
                    st.caption(f"📅 {fecha[:10]}")
                    
                    seleccionada = st.checkbox(
                        f"Seleccionar para eliminar",
                        key=f"select_{img_id}",
                        value=img_id in st.session_state.imagenes_seleccionadas
                    )
                    
                    if seleccionada:
                        st.session_state.imagenes_seleccionadas.add(img_id)
                    elif img_id in st.session_state.imagenes_seleccionadas:
                        st.session_state.imagenes_seleccionadas.remove(img_id)
                    
                    if st.button("📄 Cargar texto", key=f"load_{img_id}", use_container_width=True):
                        st.session_state.texto_extraido = texto
                        st.session_state.texto_traducido = ""
                        st.success("Texto cargado para traducir")
                        st.rerun()
                    
                    if st.button("🗑️ Eliminar", key=f"delete_{img_id}", type="secondary", use_container_width=True):
                        try:
                            if eliminar_imagen(img_id, st.session_state.usuario_id):
                                st.success("✅ Imagen eliminada")
                                st.rerun()
                            else:
                                st.error("❌ No se pudo eliminar la imagen")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                st.divider()

# ======================================================
# TAB ASISTENTE IA (sin cambios)
# ======================================================
with tab_asistente:
    st.title("🤖 Asistente IA para Imágenes")
    st.markdown("Sube una imagen y el asistente IA generará descripciones y análisis detallados.")
    
    col_upload, col_preview = st.columns(2)
    
    with col_upload:
        st.subheader("📤 Subir imagen")
        imagen_asistente = st.file_uploader(
            "Selecciona una imagen para analizar",
            type=["png", "jpg", "jpeg"],
            key="asistente_uploader"
        )
        
        st.subheader("⚙️ Configuración del análisis")
        
        nivel_detalle = st.radio(
            "Nivel de detalle de la descripción:",
            ["breve", "normal", "detallado"],
            horizontal=True
        )
        
        tipo_analisis = st.selectbox(
            "Tipo de análisis avanzado:",
            ["general", "tecnico", "artistico", "emocional"],
            help="Selecciona el tipo de análisis que deseas"
        )
        
        col_btn_desc, col_btn_anal = st.columns(2)
        with col_btn_desc:
            btn_descripcion = st.button(
                "📝 Generar descripción", 
                type="primary", 
                use_container_width=True,
                disabled=not imagen_asistente
            )
        
        with col_btn_anal:
            btn_analisis = st.button(
                "🔬 Análisis avanzado", 
                type="secondary", 
                use_container_width=True,
                disabled=not imagen_asistente
            )
    
    with col_preview:
        if imagen_asistente:
            st.subheader("👁️ Vista previa")
            st.image(imagen_asistente, use_container_width=True, caption="Imagen para análisis")
            
            imagen_asistente.seek(0, 2)
            tamaño_bytes = imagen_asistente.tell()
            imagen_asistente.seek(0)
            
            st.caption(f"Tamaño: {tamaño_bytes / 1024:.1f} KB")
    
    if btn_descripcion and imagen_asistente:
        with st.spinner("🤖 Generando descripción..."):
            try:
                descripcion = describir_imagen(
                    imagen_asistente,
                    API_KEY,
                    nivel_detalle
                )
                st.session_state.descripcion_imagen = descripcion
                
                imagen_asistente.seek(0)
                guardar_imagen(
                    usuario_id=st.session_state.usuario_id,
                    imagen_bytes=imagen_asistente.getvalue(),
                    texto_original=f"DESCRIPCIÓN ({nivel_detalle}):\n{descripcion}"
                )
                
                st.success("✅ Descripción generada y guardada")
            except Exception as e:
                st.error(f"❌ Error al generar descripción: {str(e)}")
    
    if st.session_state.descripcion_imagen:
        st.subheader("📝 Descripción generada")
        
        with st.container(border=True):
            col_header_desc, col_copy_desc = st.columns([4, 1])
            with col_header_desc:
                st.markdown(f"**Nivel de detalle:** {nivel_detalle.capitalize()}")
            with col_copy_desc:
                if st.button("📋 Copiar", key="copiar_descripcion", use_container_width=True):
                    st.write(f"""<script>
                        navigator.clipboard.writeText(`{st.session_state.descripcion_imagen.replace('`', '\\`')}`);
                    </script>""", unsafe_allow_html=True)
                    st.toast("✅ Descripción copiada al portapapeles", icon="📋")
            
            st.markdown(st.session_state.descripcion_imagen)
            
            palabras_desc = len(st.session_state.descripcion_imagen.split())
            st.caption(f"📊 {palabras_desc} palabras | {len(st.session_state.descripcion_imagen)} caracteres")
    
    if btn_analisis and imagen_asistente:
        with st.spinner("🔬 Realizando análisis avanzado..."):
            try:
                analisis = analizar_imagen_avanzado(
                    imagen_asistente,
                    API_KEY,
                    tipo_analisis
                )
                st.session_state.analisis_avanzado = analisis
                
                imagen_asistente.seek(0)
                guardar_imagen(
                    usuario_id=st.session_state.usuario_id,
                    imagen_bytes=imagen_asistente.getvalue(),
                    texto_original=f"ANÁLISIS ({tipo_analisis}):\n{analisis}"
                )
                
                st.success("✅ Análisis avanzado generado y guardado")
            except Exception as e:
                st.error(f"❌ Error al generar análisis: {str(e)}")
    
    if st.session_state.analisis_avanzado:
        st.subheader(f"🔬 Análisis {tipo_analisis.capitalize()}")
        
        with st.container(border=True):
            col_header_anal, col_copy_anal = st.columns([4, 1])
            with col_header_anal:
                st.markdown(f"**Tipo de análisis:** {tipo_analisis.capitalize()}")
            with col_copy_anal:
                if st.button("📋 Copiar", key="copiar_analisis", use_container_width=True):
                    st.write(f"""<script>
                        navigator.clipboard.writeText(`{st.session_state.analisis_avanzado.replace('`', '\\`')}`);
                    </script>""", unsafe_allow_html=True)
                    st.toast("✅ Análisis copiado al portapapeles", icon="📋")
            
            st.markdown(st.session_state.analisis_avanzado)
            
            palabras_anal = len(st.session_state.analisis_avanzado.split())
            st.caption(f"📊 {palabras_anal} palabras | {len(st.session_state.analisis_avanzado)} caracteres")

# ======================================================
# TAB PERFIL (sin cambios)
# ======================================================
with tab_perfil:
    st.title("👤 Mi Perfil")
    
    datos_usuario = obtener_datos_usuario(st.session_state.usuario_id)
    estadisticas = obtener_estadisticas_usuario(st.session_state.usuario_id)
    
    col_perfil, col_stats = st.columns(2)
    
    with col_perfil:
        st.subheader("📋 Datos del Perfil")
        
        with st.container():
            st.markdown("### Información Personal")
            
            if datos_usuario:
                st.info(f"**📧 Email:** {datos_usuario['email']}")
                
                fecha_registro = datos_usuario['fecha_registro']
                if fecha_registro:
                    try:
                        fecha_obj = datetime.fromisoformat(fecha_registro.replace('Z', '+00:00'))
                        fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M")
                    except:
                        fecha_formateada = fecha_registro
                    
                    st.info(f"**📅 Fecha de registro:** {fecha_formateada}")
                
                if fecha_registro:
                    try:
                        fecha_registro_obj = datetime.fromisoformat(fecha_registro.replace('Z', '+00:00'))
                        dias_miembro = (datetime.now() - fecha_registro_obj).days
                        st.info(f"**⏳ Miembro desde hace:** {dias_miembro} días")
                    except:
                        pass
        
        st.subheader("🔐 Cambiar Contraseña")
        
        with st.form("form_cambiar_password"):
            password_actual = st.text_input("Contraseña actual", type="password")
            nueva_password = st.text_input("Nueva contraseña", type="password")
            confirmar_password = st.text_input("Confirmar nueva contraseña", type="password")
            
            cambiar = st.form_submit_button("🔄 Cambiar contraseña")
            
            if cambiar:
                if not password_actual:
                    st.error("❌ Debes ingresar tu contraseña actual")
                elif not nueva_password:
                    st.error("❌ Debes ingresar una nueva contraseña")
                elif nueva_password != confirmar_password:
                    st.error("❌ Las contraseñas no coinciden")
                else:
                    try:
                        if cambiar_contraseña(st.session_state.usuario_id, password_actual, nueva_password):
                            st.success("✅ Contraseña cambiada exitosamente")
                        else:
                            st.error("❌ Error al cambiar la contraseña")
                    except ValueError as e:
                        st.error(str(e))
    
    with col_stats:
        st.subheader("📊 Estadísticas de Uso")
        
        col_metric1, col_metric2 = st.columns(2)
        
        with col_metric1:
            st.metric(
                label="📸 Imágenes procesadas",
                value=estadisticas.get("total_imagenes", 0)
            )
        
        with col_metric2:
            if estadisticas.get("ultima_actividad"):
                try:
                    fecha_ultima = datetime.fromisoformat(
                        estadisticas["ultima_actividad"].replace('Z', '+00:00')
                    )
                    dias_desde = (datetime.now() - fecha_ultima).days
                    st.metric(
                        label="🕐 Última actividad",
                        value=f"Hace {dias_desde} días"
                    )
                except:
                    st.metric(
                        label="🕐 Última actividad",
                        value="Reciente"
                    )
        
        if estadisticas.get("actividad_30_dias"):
            st.markdown("### 📈 Actividad (últimos 30 días)")
            
            datos_actividad = estadisticas["actividad_30_dias"]
            if datos_actividad:
                fechas = [d["fecha"] for d in datos_actividad]
                cantidades = [d["cantidad"] for d in datos_actividad]
                
                fig = px.bar(
                    x=fechas,
                    y=cantidades,
                    labels={'x': 'Fecha', 'y': 'Imágenes procesadas'},
                    title="Actividad por día"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🌍 Idiomas más usados")
        idiomas_data = analizar_idiomas_usuario(st.session_state.usuario_id)
        
        if idiomas_data:
            fig = px.pie(
                names=[d["idioma"] for d in idiomas_data],
                values=[d["cantidad"] for d in idiomas_data],
                title="Distribución de idiomas"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no hay datos suficientes sobre los idiomas usados")
    
    st.subheader("📤 Exportar mis datos")
    
    with st.container():
        st.markdown("""
        Puedes exportar todos tus datos en formato JSON. Esto incluye:
        - Información de tu perfil
        - Todas las imágenes procesadas
        - Textos extraídos
        - Estadísticas de uso
        """)
        
        col_exp1, col_exp2 = st.columns([3, 1])
        
        with col_exp1:
            st.info("Los datos se exportarán en formato JSON listos para descargar")
        
        with col_exp2:
            if st.button("📥 Exportar datos JSON", type="primary", use_container_width=True):
                try:
                    datos_exportar = exportar_datos_usuario(st.session_state.usuario_id)
                    
                    json_str = json.dumps(datos_exportar, indent=2, ensure_ascii=False)
                    
                    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo = f"datos_usuario_{st.session_state.usuario_id}_{fecha_actual}.json"
                    
                    st.download_button(
                        label="⬇️ Descargar archivo JSON",
                        data=json_str,
                        file_name=nombre_archivo,
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    st.success("✅ Datos exportados exitosamente")
                    
                except Exception as e:
                    st.error(f"❌ Error al exportar datos: {str(e)}")

# =========================
# FOOTER
# =========================
st.divider()
st.caption("🤖 AI Content Studio | Proyecto AI-DRIVEN SOLUTIONS | CFGM Desarrollo de Aplicaciones")

# =========================
# ESTILOS CSS ADICIONALES
# =========================
st.markdown("""
<style>
/* Mejorar tarjetas de contenido social */
[data-testid="stExpander"] {
    border: 1px solid rgba(49, 51, 63, 0.2);
    border-radius: 0.5rem;
    padding: 1rem;
}

/* Botones de copiar más visibles */
.stButton > button[kind="secondary"] {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
}

.stButton > button[kind="secondary"]:hover {
    background-color: #e9ecef;
    border-color: #adb5bd;
}

/* Estilo para hashtags */
code {
    background-color: #f1f3f5;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.9em;
}

/* Animación sutil para botones */
.stButton > button {
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>

""", unsafe_allow_html=True)
