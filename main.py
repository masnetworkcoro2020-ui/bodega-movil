import streamlit as st
from supabase import create_client

# 1. LLAVES DE LA CORONA (Conexión Directa)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

st.set_page_config(page_title="Bodega Móvil", layout="centered")

# Inicializar conexión a Supabase
@st.cache_resource
def conectar_db():
    return create_client(URL, KEY)

supabase = conectar_db()

# 2. CONTROL DE ACCESO (ADN MAESTRO)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso al Sistema")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Clave", type="password")
    
    if st.button("INGRESAR", use_container_width=True):
        # Validación con tus credenciales guardadas
        if u == "jmaar" and p == "15311751":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
    st.stop()

# 3. CÓDIGO DEL INVENTARIO (Solo se ve si logueas)
st.title("📦 Control de Inventario")

# Intento de cargar el Escáner
try:
    from streamlit_barcode_scanner import st_barcode_scanner
    st.subheader("📷 Escanear Producto")
    barcode = st_barcode_scanner()
except Exception:
    barcode = None
    st.warning("Aviso: Escáner de cámara no disponible. Usa el buscador manual.")

# Buscador Manual (Siempre activo)
st.divider()
codigo_manual = st.text_input("Escribe el código de barras:", value=barcode if barcode else "")

# Lógica de Búsqueda en la Base de Datos
if codigo_manual:
    with st.spinner('Buscando en la Corona...'):
        # Buscamos en la tabla 'productos' por la columna 'codigo'
        res = supabase.table("productos").select("*").eq("codigo", codigo_manual).execute()
        
        if res.data:
            prod = res.data[0]
            st.success(f"✅ ¡Producto Encontrado: {prod['nombre']}!")
            
            # Mostramos los detalles del producto
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Precio $", f"{prod['precio_dol']}")
            with col2:
                # Si tienes columna de stock en tu tabla
                stock = prod.get('stock', 'N/D')
                st.metric("Existencia", stock)
        else:
            st.error(f"❌ El código {codigo_manual} no existe en el sistema.")

# Botón para salir
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()
