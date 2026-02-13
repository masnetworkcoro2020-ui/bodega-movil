import streamlit as st
from supabase import create_client

# --- LAS LLAVES DE LA CORONA (Extraídas de tu config.py) ---
URL_CORONA = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY_CORONA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Bodega Móvil",
    page_icon="🚀",
    layout="centered"
)

# 2. CONEXIÓN DIRECTA A SUPABASE
try:
    supabase = create_client(URL_CORONA, KEY_CORONA)
except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")
    st.stop()

# 3. CONTROL DE SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_nombre' not in st.session_state:
    st.session_state.usuario_nombre = ""

# 4. PANTALLA DE LOGIN
if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema")
    
    # Usamos tus credenciales maestras del ADN
    u = st.text_input("Usuario").strip().lower()
    p = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR", use_container_width=True):
        # A. EL SUPER USUARIO MAESTRO
        if u == "jmaar" and p == "15311751":
            st.session_state.autenticado = True
            st.session_state.usuario_nombre = "Administrador Maestro"
            st.rerun()
        
        # B. OTROS USUARIOS EN LA BASE DE DATOS
        else:
            try:
                # Buscamos en la tabla 'usuarios'
                res = supabase.table("usuarios").select("*").eq("usuario", u).execute()
                if res.data:
                    user_db = res.data[0]
                    if user_db["clave"] == p:
                        st.session_state.autenticado = True
                        st.session_state.usuario_nombre = user_db.get("nombre", u)
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta")
                else:
                    st.error("Usuario no encontrado")
            except Exception as e:
                st.error("Error al verificar usuario. Intente de nuevo.")
    st.stop()

# 5. PANTALLA PRINCIPAL
st.title(f"🚀 Bienvenido, {st.session_state.usuario_nombre}")
st.success("Conexión con Supabase establecida.")

st.info("👈 Abre el menú lateral para entrar al módulo de Inventario.")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
