import streamlit as st

# 1. Configuración básica (Esto busca la carpeta /pages automáticamente)
st.set_page_config(page_title="Bodega Movil", layout="centered")

# 2. Control de Acceso Simple
if 'login' not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Acceso")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Clave", type="password")
    
    if st.button("Entrar"):
        # Usamos tus credenciales
        if usuario == "jmaar" and clave == "15311751":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Incorrecto")
    st.stop()

# 3. Pantalla de Bienvenida
st.title("🚀 Sistema Activo")
st.success("Usa el menú de la izquierda para entrar a '1_Inventario'")
st.info("Si no ves el menú, dale a la flechita '>' arriba a la izquierda.")
