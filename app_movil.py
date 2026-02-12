import streamlit as st
from config import get_supabase
import usuarios, tasa, inventario

# Configuración
st.set_page_config(page_title="Bodega 360", layout="centered")

# Conexión
supabase = get_supabase()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    usuarios.login_screen(supabase)
else:
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    opcion = st.sidebar.radio("MENÚ", ["💰 TASA", "📦 INVENTARIO", "👤 PERFIL"])
    
    if st.sidebar.button("🚪 SALIR"):
        st.session_state.autenticado = False
        st.rerun()

    if opcion == "💰 TASA":
        tasa.mostrar(supabase)
    elif opcion == "📦 INVENTARIO":
        inventario.mostrar(supabase)
    elif opcion == "👤 PERFIL":
        usuarios.mostrar_perfil()
