import streamlit as st
from supabase import create_client

# --- CONEXIÓN SEGURA ---
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Bodega Móvil", layout="centered")

# --- CONTROL DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = ""

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso Bodega Pro")
    
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR", use_container_width=True):
        if u == "jmaar" and p == "15311751":
            st.session_state.autenticado = True
            st.session_state.usuario_actual = u
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- ESCRITORIO LIMPIO (PANTALLA BLANCA) ---
st.title("🚀 Panel de Control")
st.write(f"Bienvenido, **{st.session_state.usuario_actual}**")

# Aquí es donde pondremos los 4 botones de tus módulos
st.divider()
st.info("Selecciona un módulo para empezar (En construcción)")

col1, col2 = st.columns(2)
with col1:
    st.button("🪙 TASA BCV", use_container_width=True)
    st.button("📦 INVENTARIO", use_container_width=True)
with col2:
    st.button("🛒 VENTAS", use_container_width=True)
    st.button("📊 HISTORIAL", use_container_width=True)

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
