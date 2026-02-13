import streamlit as st

st.set_page_config(page_title="Bodega - Panel", layout="centered")

# --- ADN DE SEGURIDAD ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 Acceso</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuario").lower().strip()
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("INGRESAR", use_container_width=True):
            if u == "jmaar" and p == "15311751":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Error de acceso")
    st.stop()

# --- PANEL DE CONTROL (Imagen 2) ---
st.markdown(f"### ⚡ Bienvenido, JMAAR")
st.title("🕹️ Panel de Control")
st.write("Selecciona el módulo que deseas operar hoy:")

col1, col2 = st.columns(2)

with col1:
    if st.button("📦 ABRIR INVENTARIO", use_container_width=True, height=100):
        st.session_state.pagina = "inventario"
        st.rerun()

with col2:
    if st.button("🪙 CONSULTAR TASA BCV", use_container_width=True, height=100):
        st.session_state.pagina = "tasa"
        st.rerun()

# Lógica de navegación interna para evitar errores de archivo
if 'pagina' in st.session_state:
    if st.session_state.pagina == "inventario":
        st.switch_page("inventario.py")
    elif st.session_state.pagina == "tasa":
        st.switch_page("tasa_bcv.py")
