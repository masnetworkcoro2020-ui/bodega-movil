import streamlit as st
from config import get_supabase
import tasa, inventario, usuarios # Asegúrate que NO haya espacios antes de 'import'

# El resto del código también debe empezar desde el borde
supabase = get_supabase()

# Configuración inicial
st.set_page_config(page_title="BODEGA 360", layout="centered")

# --- CONTROL DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    usuarios.login_screen(supabase)
    st.stop()

# --- SI ESTÁ LOGUEADO ---
st.sidebar.title(f"👤 {st.session_state.get('usuario_actual', 'Usuario')}")
opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.autenticado = False
    st.rerun()

if opcion == "💰 TASA":
    tasa.mostrar(supabase)
elif opcion == "📦 INVENTARIO":
    inventario.mostrar(supabase)
elif opcion == "👥 USUARIOS":
    usuarios.mostrar(supabase)
