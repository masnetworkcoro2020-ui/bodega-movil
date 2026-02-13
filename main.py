import streamlit as st
from supabase import create_client

# --- CONEXIÓN DIRECTA (DATOS RECUPERADOS) ---
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Bodega Móvil", layout="centered")

# --- CONTROL DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso Bodega Pro")
    
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR", use_container_width=True):
        # Validación con tus datos maestros
        if u == "jmaar" and p == "15311751":
            st.session_state.autenticado = True
            st.session_state.usuario_actual = u
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- PANEL DE CONTROL (LOS 4 MÓDULOS) ---
st.title("🚀 Panel de Control")
st.write(f"Bienvenido: **{st.session_state.usuario_actual}**")
st.divider()

# Grid de 2x2 para los botones
col1, col2 = st.columns(2)

with col1:
    if st.button("🪙 TASA BCV", use_container_width=True):
        st.session_state.modulo = "tasa"
    if st.button("📦 INVENTARIO", use_container_width=True):
        st.session_state.modulo = "inventario"

with col2:
    if st.button("👥 USUARIOS", use_container_width=True):
        st.session_state.modulo = "usuarios"
    if st.button("📊 HISTORIAL", use_container_width=True):
        st.session_state.modulo = "historial"

# --- ZONA DE TRABAJO (BLANCA) ---
st.write("---")
if 'modulo' not in st.session_state:
    st.info("Selecciona un módulo arriba para empezar a trabajar.")
else:
    if st.session_state.modulo == "tasa":
        st.subheader("Módulo: Tasa BCV")
        st.write("Aquí actualizaremos la tasa en Supabase...")
        
    elif st.session_state.modulo == "inventario":
        st.subheader("Módulo: Inventario")
        st.write("Aquí gestionaremos tus productos...")
        
    elif st.session_state.modulo == "usuarios":
        st.subheader("Módulo: Gestión de Usuarios")
        st.write("Aquí podrás crear y editar accesos...")
        
    elif st.session_state.modulo == "historial":
        st.subheader("Módulo: Historial")
        st.write("Consulta de movimientos registrados...")

# Botón para salir en el lateral
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
