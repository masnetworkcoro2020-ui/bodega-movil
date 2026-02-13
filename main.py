import streamlit as st
from supabase import create_client

# 1. Configuración de la Corona y la Página
URL_CORONA = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY_CORONA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

st.set_page_config(page_title="Bodega Móvil", layout="centered", initial_sidebar_state="collapsed")

# 2. Estilo para ESCONDER el menú lateral si no está logueado
if 'conectado' not in st.session_state or not st.session_state.conectado:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Acceso (ADN Maestro)
if 'conectado' not in st.session_state:
    st.session_state.conectado = False

if not st.session_state.conectado:
    st.title("🔐 Acceso Privado")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    
    if st.button("ENTRAR"):
        if u == "jmaar" and p == "15311751":
            st.session_state.conectado = True
            st.rerun()
        else:
            st.error("Acceso denegado")
    st.stop()

# 4. PANTALLA DE BIENVENIDA (Solo se ve al loguearse)
st.title("🚀 Panel de Control")
st.success(f"Bienvenido, {u if 'u' in locals() else 'Administrador'}")

st.info("👈 Ahora puedes ver el menú a la izquierda para ir a Inventario.")

# Botón para salir
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.conectado = False
    st.rerun()
