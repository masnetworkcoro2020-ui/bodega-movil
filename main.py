import streamlit as st

st.set_page_config(page_title="Acceso Bodega", layout="centered")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Bodega Pro V2")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Clave", type="password")
    
    if st.button("INGRESAR"):
        if u == "jmaar" and p == "15311751": # ADN Maestro
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- MENÚ DE BIENVENIDA ---
st.title(f"🚀 Panel Principal")
st.write(f"Bienvenido, **{u if 'u' in locals() else 'Administrador'}**")

col1, col2 = st.columns(2)
with col1:
    if st.button("📦 Ir a Inventario", use_container_width=True):
        st.switch_page("inventario.py")
with col2:
    if st.button("🪙 Ver Tasa BCV", use_container_width=True):
        st.switch_page("tasa_bcv.py")
