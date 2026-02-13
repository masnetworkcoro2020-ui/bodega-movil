import streamlit as st

st.set_page_config(page_title="Bodega Móvil - Acceso", layout="centered")

# --- SEGURIDAD ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- VISTA 1: LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 Acceso Administrativo</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("Usuario Manager").lower().strip()
        p = st.text_input("Contraseña Maestra", type="password")
        if st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True):
            if u == "jmaar" and p == "15311751": # Tus datos originales
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# --- VISTA 2: PANEL DE CONTROL (Corregido sin error de height) ---
st.markdown(f"### ⚡ Bienvenido, {st.session_state.user.upper()}")
st.title("🕹️ Panel de Control")
st.write("Selecciona el módulo que deseas operar hoy:")

st.divider()

col1, col2 = st.columns(2)

with col1:
    # Quitamos 'height=100' para que no de error en tu servidor
    if st.button("📦 ABRIR INVENTARIO", use_container_width=True):
        st.switch_page("inventario.py")

with col2:
    if st.button("🪙 CONSULTAR TASA BCV", use_container_width=True):
        st.switch_page("tasa_bcv.py")

st.divider()

if st.sidebar.button("🔴 Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()
