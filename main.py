import streamlit as st

# Configuración de página (Esto es lo que activa el reconocimiento de la carpeta pages)
st.set_page_config(
    page_title="Bodega Pro",
    page_icon="🚀",
    layout="centered"
)

# --- CONTROL DE ACCESO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema")
    # Usamos tus credenciales maestras
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR", use_container_width=True):
        if u == "jmaar" and p == "15311751":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- SI ESTÁ AUTENTICADO ---
st.title("🚀 Panel de Control")
st.write(f"Bienvenido, **{u if 'u' in locals() else 'Usuario'}**")

st.info("👈 Mira a la izquierda: Selecciona '1 Inventario' para empezar.")

# Botón para cerrar sesión en la barra lateral
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
