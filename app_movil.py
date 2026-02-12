import streamlit as st
from config import get_supabase
import usuarios, tasa, inventario

# Configuración de página
st.set_page_config(page_title="Bodega 360", layout="centered")

# Conexión a Supabase
supabase = get_supabase()

# Control de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    usuarios.login_screen(supabase)
else:
    # Menú lateral
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["💰 TASA BCV", "📦 INVENTARIO", "👤 MI PERFIL"])
    
    if st.sidebar.button("🚪 CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()

    # Carga de módulos
    if opcion == "💰 TASA BCV":
        tasa.mostrar(supabase)
    elif opcion == "📦 INVENTARIO":
        inventario.mostrar(supabase)
    elif opcion == "👤 MI PERFIL":
        usuarios.mostrar_perfil()
