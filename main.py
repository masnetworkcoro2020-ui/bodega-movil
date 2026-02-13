import streamlit as st

st.set_page_config(page_title="Acceso Bodega", layout="centered")

# --- ADN DE ACCESO ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso al Sistema")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("INGRESAR"):
        if u == "jmaar" and p == "15311751":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- SI YA ESTÁ LOGUEADO ---
st.title("🚀 Panel Principal")
col1, col2 = st.columns(2)

with col1:
    if st.button("📦 Ir a Inventario", use_container_width=True):
        st.switch_page("inventario.py") # Salto al archivo independiente

with col2:
    if st.button("🪙 Ver Tasa BCV", use_container_width=True):
        st.switch_page("tasa_bcv.py")
