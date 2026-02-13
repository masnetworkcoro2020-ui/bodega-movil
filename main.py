import streamlit as st

# Configuración de página limpia
st.set_page_config(page_title="Bodega Móvil - Acceso", layout="centered")

# --- ADN DE SEGURIDAD (Estado de Sesión) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- VISTA 1: EL LOGIN (Solo Admin) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔐 Acceso Administrativo</h1>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        u = st.text_input("Usuario Manager").lower().strip()
        p = st.text_input("Contraseña Maestra", type="password")
        submit = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
        
        if submit:
            # Tu usuario y clave originales
            if u == "jmaar" and p == "15311751":
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciales no autorizadas")
    st.stop()

# --- VISTA 2: EL PANEL DE CONTROL (Después de entrar) ---
st.markdown(f"### ⚡ Bienvenido, {st.session_state.user.upper()}")
st.title("🕹️ Panel de Control")
st.write("Selecciona el módulo que deseas operar hoy:")

st.divider()

# Botones grandes para el Panel
col1, col2 = st.columns(2)

with col1:
    if st.button("📦 ABRIR INVENTARIO", use_container_width=True, height=100):
        st.switch_page("inventario.py")

with col2:
    if st.button("🪙 CONSULTAR TASA BCV", use_container_width=True, height=100):
        st.switch_page("tasa_bcv.py")

st.divider()

# Botón de salida en el sidebar
if st.sidebar.button("🔴 Cerrar Sesión Segura"):
    st.session_state.auth = False
    st.session_state.user = None
    st.rerun()
