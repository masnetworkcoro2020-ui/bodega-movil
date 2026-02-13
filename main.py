import streamlit as st
from supabase import create_client

# 1. LLAVES DE LA CORONA (Conexión)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

@st.cache_resource
def init_supabase():
    return create_client(URL, KEY)

supabase = init_supabase()

# 2. CONTROL DE ACCESO MAESTRO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso al Sistema")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("INGRESAR"):
        if u == "jmaar" and p == "15311751":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. NAVEGADOR DE MÓDULOS (Sustituye a switch_page para evitar errores)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "panel"

# Barra Lateral de Navegación
with st.sidebar:
    st.title("📌 Menú")
    if st.button("🏠 Panel Principal"): st.session_state.pagina = "panel"
    if st.button("📦 Inventario"): st.session_state.pagina = "inventario"
    if st.button("🪙 Tasa BCV"): st.session_state.pagina = "tasa"
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

# ==========================================
# MÓDULO: PANEL PRINCIPAL
# ==========================================
if st.session_state.pagina == "panel":
    st.title("🚀 Panel de Control")
    st.write("Bienvenido. Selecciona una herramienta en el menú lateral.")

# ==========================================
# MÓDULO: INVENTARIO (VA SOLO AQUÍ)
# ==========================================
elif st.session_state.pagina == "inventario":
    st.title("📦 Control de Inventario")
    
    # 1. EL ESCÁNER (Línea para activar cámara si decides instalar la librería)
    # try: from streamlit_barcode_scanner import st_barcode_scanner; barcode = st_barcode_scanner()
    # except: barcode = None
    
    # 2. BUSCADOR
    codigo = st.text_input("Escribe el código de barras:")
    
    if codigo:
        with st.spinner('Consultando a la Corona...'):
            res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
            if res.data:
                p = res.data[0]
                st.success(f"✅ PRODUCTO: {p['nombre']}")
                st.metric("PRECIO $", f"{p['precio_dol']}")
                st.write(f"Stock actual: {p.get('stock', 'N/D')}")
            else:
                st.error("🚫 Código no encontrado.")

# ==========================================
# MÓDULO: TASA BCV
# ==========================================
elif st.session_state.pagina == "tasa":
    st.title("🪙 Tasa BCV")
    res_tasa = supabase.table("ajustes").select("valor").eq("parametro", "tasa_bcv").execute()
    if res_tasa.data:
        st.metric("Dólar BCV", f"{res_tasa.data[0]['valor']} BS")
