import streamlit as st
from supabase import create_client

# 1. LLAVES DE LA CORONA
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

st.set_page_config(page_title="Bodega Móvil", layout="centered")

# 2. CONEXIÓN
@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# 3. SESIÓN Y LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Maestro")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Clave", type="password")
    
    if st.button("ENTRAR"):
        if u == "jmaar" and p == "15311751": # ADN Maestro
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# 4. SI ESTÁ LOGUEADO -> MUESTRA EL INVENTARIO DIRECTO
st.title("📦 Inventario Bodega")

try:
    from streamlit_barcode_scanner import st_barcode_scanner
    st.subheader("📷 Escáner Activo")
    barcode = st_barcode_scanner()
    
    if barcode:
        st.info(f"Código detectado: {barcode}")
        # Búsqueda en Supabase
        res = supabase.table("productos").select("*").eq("codigo", barcode).execute()
        if res.data:
            p = res.data[0]
            st.success(f"Producto: {p['nombre']}")
            st.metric("Precio $", f"{p['precio_dol']}")
        else:
            st.warning("No registrado")
except Exception as e:
    st.error("Error cargando el componente de cámara.")
    st.info("Usa el buscador manual abajo.")

st.divider()
manual = st.text_input("Buscador Manual")
if manual:
    # Lógica de búsqueda manual igual a la de arriba
    pass

if st.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()
