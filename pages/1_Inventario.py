import streamlit as st
from supabase import create_client

# 1. EL CANDADO DE SEGURIDAD (Para que no entren sin login)
if 'conectado' not in st.session_state or not st.session_state.conectado:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    st.stop()

# 2. INTENTO DE CARGA DEL ESCÁNER
try:
    from streamlit_barcode_scanner import st_barcode_scanner
    escaner_disponible = True
except ImportError:
    escaner_disponible = False

# 3. CONEXIÓN A LA CORONA
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.title("📦 Control de Inventario")

# 4. LÓGICA DEL ESCÁNER
codigo = None

if escaner_disponible:
    st.subheader("📷 Escanear Código")
    # El escáner se activa aquí
    barcode = st_barcode_scanner()
    if barcode:
        codigo = barcode
else:
    st.error("❌ El componente del escáner no se instaló correctamente en el servidor.")

# 5. BUSCADOR MANUAL (Siempre disponible por si acaso)
st.divider()
manual = st.text_input("O escribe el código manualmente:", value=codigo if codigo else "")
if manual:
    codigo = manual

# 6. BÚSQUEDA EN SUPABASE
if codigo:
    st.info(f"Buscando: {codigo}...")
    res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
    if res.data:
        prod = res.data[0]
        st.success(f"✅ ¡Encontrado: {prod['nombre']}!")
        col1, col2 = st.columns(2)
        col1.metric("Precio $", f"{prod['precio_dol']}")
        col2.metric("Stock", f"{prod.get('stock', 0)}")
    else:
        st.error("🚫 Producto no registrado en la base de datos.")
