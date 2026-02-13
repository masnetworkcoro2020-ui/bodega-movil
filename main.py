import streamlit as st

# Configuración inicial
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
        if u == "jmaar" and p == "15311751":
            st.session_state.autenticado = True
            st.session_state.usuario_actual = u
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- PANEL PRINCIPAL ---
st.title("🚀 Panel de Control")
st.write(f"Bienvenido: **{st.session_state.usuario_actual}**")
st.info("👈 Selecciona un módulo en el menú de la izquierda para trabajar.")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
