import streamlit as st
from supabase import create_client

# SEGURIDAD: Si intentan entrar directo por link sin loguearse en main
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("main.py")

# LLAVES DE LA CORONA
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.title("📦 Módulo de Inventario")

if st.button("⬅️ Volver al Menú"):
    st.switch_page("main.py")

st.divider()

# BUSCADOR
codigo = st.text_input("Escribe el código de barras:")

if codigo:
    res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
    if res.data:
        p = res.data[0]
        st.success(f"Producto: {p['nombre']}")
        st.metric("Precio $", f"{p['precio_dol']}")
    else:
        st.error("No registrado en la base de datos.")
