import streamlit as st
from supabase import create_client
from camera_input_live import camera_input_live
from pyzbar.pyzbar import decode
from PIL import Image

# Candado de Seguridad
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("main.py")

# Conexión a la Corona
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.title("📦 Inventario Bodega")
if st.button("⬅️ Volver"):
    st.switch_page("main.py")

# --- ESCÁNER EN VIVO ---
st.subheader("📷 Escanear")
imagen_viva = camera_input_live()

codigo_final = None

if imagen_viva:
    pil_img = Image.open(imagen_viva)
    resultado = decode(pil_img)
    if resultado:
        codigo_final = resultado[0].data.decode('utf-8')
        st.success(f"Código detectado: {codigo_final}")

# Buscador manual por si la cámara falla
manual = st.text_input("O escribe el código:", value=codigo_final if codigo_final else "")

if manual:
    res = supabase.table("productos").select("*").eq("codigo", manual).execute()
    if res.data:
        p = res.data[0]
        st.info(f"Producto: {p['nombre']} | Precio: {p['precio_dol']}$")
    else:
        st.error("No encontrado en la Corona.")
