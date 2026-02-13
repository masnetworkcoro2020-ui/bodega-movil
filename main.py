import streamlit as st
from supabase import create_client

# 1. LLAVES DE LA CORONA
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
        if u == "jmaar" and p == "15311751":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
    st.stop()

# 3. MÓDULO DE INVENTARIO (Aquí está el código que pediste)
st.title("📦 Inventario Bodega")
st.write("---")

# Buscador Manual (El más estable para evitar errores de cámara)
codigo_manual = st.text_input("Escribe el código de barras:")

if codigo_manual:
    with st.spinner('Buscando en la Corona...'):
        # Consultamos la tabla 'productos' por la columna 'codigo'
        res = supabase.table("productos").select("*").eq("codigo", codigo_manual).execute()
        
        if res.data:
            prod = res.data[0]
            st.success(f"✅ ¡Producto Encontrado: {prod['nombre']}!")
            
            # Mostramos los detalles en columnas bonitas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Precio $", f"{prod['precio_dol']}")
            with col2:
                stock = prod.get('stock', 'N/D')
                st.metric("Existencia", stock)
        else:
            st.error(f"❌ El código {codigo_manual} no está en la base de datos.")

# Botón para cerrar sesión en la parte de abajo
st.write("---")
if st.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()
