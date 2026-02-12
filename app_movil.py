import streamlit as st
from config import get_supabase
import tasa, inventario, usuarios # Importamos los otros archivos .py

supabase = get_supabase()

# Configuración para móvil
st.set_page_config(page_title="BODEGA 360", layout="centered")

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    usuarios.login_screen(supabase)
    st.stop()

# --- MENÚ DE BOTONES (Estilo móvil) ---
st.sidebar.title("MENÚ")
opcion = st.sidebar.radio("Ir a:", ["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

if opcion == "💰 TASA":
    tasa.mostrar(supabase)
elif opcion == "📦 INVENTARIO":
    inventario.mostrar(supabase)
elif opcion == "👥 USUARIOS":
    usuarios.mostrar(supabase)
