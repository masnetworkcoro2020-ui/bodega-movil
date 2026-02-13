import streamlit as st
from supabase import create_client

# --- LLAVES DE LA CORONA (Conexión Directa) ---
URL_CORONA = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY_CORONA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

# Configuración básica de la página
st.set_page_config(page_title="Bodega Móvil", layout="centered")

# Intentar conexión con Supabase
try:
    supabase = create_client(URL_CORONA, KEY_CORONA)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- LÓGICA DE ACCESO ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False

if not st.session_state.conectado:
    st.title("🔐 Acceso Maestro")
    
    # Datos del ADN: jmaar / 15311751
    user = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("ENTRAR", use_container_width=True):
        if user == "jmaar" and clave == "15311751":
            st.session_state.conectado = True
            st.rerun()
        else:
            # Opción B: Buscar en Supabase si no es el maestro
            try:
                res = supabase.table("usuarios").select("*").eq("usuario", user).execute()
                if res.data and res.data[0]["clave"] == clave:
                    st.session_state.conectado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            except:
                st.error("Error validando usuario")
    st.stop()

# --- PANTALLA SI LOGRA ENTRAR ---
st.title("🚀 Sistema Bodega Móvil")
st.success("¡Felicidades mano! El motor principal está encendido y conectado a la Corona.")
st.write(f"Bienvenido de nuevo, **{user if 'user' in locals() else 'JMaar'}**.")

st.info("Ahorita no ves el menú porque borramos la carpeta. Avisame cuando veas este mensaje para crear el primer módulo paso a paso.")

if st.button("Cerrar Sesión"):
    st.session_state.conectado = False
    st.rerun()
