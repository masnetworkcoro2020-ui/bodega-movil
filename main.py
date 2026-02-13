import streamlit as st
from supabase import create_client

# --- CONEXIÓN RECUPERADA DE TU CONFIG.PY ---
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# Configuración de página para que se vea bien en celular
st.set_page_config(page_title="Bodega Móvil", layout="centered")

# --- LÓGICA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema")
    st.write("Introduce tus credenciales para continuar")
    
    # Campos de entrada con tus datos maestros
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR", use_container_width=True):
        # Validación con tus datos originales
        if usuario == "jmaar" and clave == "15311751":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos. Intenta de nuevo.")
    
    st.stop() # Detiene el código aquí si no se ha logueado

# --- PANTALLA EN BLANCO (LISTA PARA LOS 4 MÓDULOS) ---
st.success(f"¡Bienvenido, {usuario}! Sesión iniciada.")
st.write("Has ingresado correctamente. El escritorio está limpio para empezar a montar los módulos.")

if st.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
