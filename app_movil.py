import streamlit as st
from config import get_supabase
import tasa, inventario, usuarios # Tus 3 módulos

supabase = get_supabase()

# Configuración inicial
st.set_page_config(page_title="BODEGA 360", layout="centered")

# --- CONTROL DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    usuarios.login_screen(supabase)
    st.stop() # Detiene la ejecución aquí si no está logueado

# --- SI ESTÁ LOGUEADO, MUESTRA EL MENÚ ---
st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.autenticado = False
    st.rerun()

# Cargar el módulo seleccionado
if opcion == "💰 TASA":
    tasa.mostrar(supabase)
elif opcion == "📦 INVENTARIO":
    inventario.mostrar(supabase)
elif opcion == "👥 USUARIOS":
    usuarios.mostrar(supabase)
