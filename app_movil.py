import streamlit as st
from config import get_supabase
import usuarios, tasa, inventario

# 1. Configuración de página optimizada para móvil
st.set_page_config(page_title="Bodega 360", layout="centered", initial_sidebar_state="collapsed")

# 2. Conectar a tu base de datos (con tus llaves de config.py)
supabase = get_supabase()

# 3. Inicializar el estado de la sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- FLUJO DE SEGURIDAD ---
if not st.session_state.autenticado:
    usuarios.login_screen(supabase)
else:
    # --- MENÚ PRINCIPAL UNA VEZ LOGUEADO ---
    st.sidebar.image("logotipo.png", width=150)
    st.sidebar.title(f"Hola, {st.session_state.usuario_actual}")
    
    opcion = st.sidebar.radio("IR A:", ["💰 TASA BCV", "📦 INVENTARIO", "👤 MI PERFIL"])
    
    if st.sidebar.button("🚪 SALIR"):
        st.session_state.autenticado = False
        st.rerun()

    # --- CARGA DE MÓDULOS ---
    if opcion == "💰 TASA BCV":
        tasa.mostrar(supabase)
    elif opcion == "📦 INVENTARIO":
        inventario.mostrar(supabase)
    elif opcion == "👤 MI PERFIL":
        usuarios.mostrar_perfil()
