
import streamlit as st
from supabase import create_client

# 1. CANDADO DE SEGURIDAD (Obliga a pasar por el login del main.py)
if 'auth' not in st.session_state or not st.session_state.auth:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión primero.")
    if st.button("Ir al Login"):
        st.switch_page("main.py")
    st.stop()

# 2. CONEXIÓN A LA CORONA
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.title("📦 Inventario Bodega")

# Botón para volver al menú principal
if st.button("⬅️ Volver al Menú"):
    st.switch_page("main.py")

st.divider()

# 3. LÓGICA DEL ESCÁNER CON PROTECCIÓN
codigo_detectado = None
try:
    from streamlit_barcode_scanner import st_barcode_scanner
    st.subheader("📷 Escanear con Cámara")
    # Esta es la línea que activa el escáner
    barcode = st_barcode_scanner()
    if barcode:
        codigo_detectado = barcode
except Exception:
    st.error("❌ El escáner de cámara no está disponible en este momento.")
    st.info("Puedes usar el buscador manual aquí abajo.")

# 4. BUSCADOR MANUAL (Siempre funciona)
manual = st.text_input("Escribe o pega el código de barras:", value=codigo_detectado if codigo_detectado else "")

# 5. BÚSQUEDA EN LA BASE DE DATOS
if manual:
    with st.spinner('Buscando producto...'):
        res = supabase.table("productos").select("*").eq("codigo", manual).execute()
        if res.data:
            p = res.data[0]
            st.success(f"✅ ¡Encontrado: {p['nombre']}!")
            col1, col2 = st.columns(2)
            col1.metric("Precio $", f"{p['precio_dol']}")
            col2.metric("Existencia", p.get('stock', 'N/D'))
        else:
            st.error("🚫 Producto no registrado.")
