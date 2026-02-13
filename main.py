import streamlit as st
from supabase import create_client

# 1. CONEXIÓN A LA CORONA
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("INGRESAR"):
        if u == "jmaar" and p == "15311751":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. MENÚ DE NAVEGACIÓN (En lugar de switch_page)
menu = st.sidebar.radio("Menú", ["Panel Principal", "Inventario", "Tasa BCV"])

if menu == "Panel Principal":
    st.title("🚀 Panel Principal")
    st.write("Bienvenido, Administrador.")

elif menu == "Inventario":
    st.title("📦 Inventario")
    # Aquí pegas la lógica de búsqueda que ya teníamos
    codigo = st.text_input("Código de barras:")
    if codigo:
        res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
        if res.data:
            st.success(f"Producto: {res.data[0]['nombre']}")
        else:
            st.error("No encontrado")

elif menu == "Tasa BCV":
    st.title("🪙 Tasa BCV")
    # Lógica de la tasa...
