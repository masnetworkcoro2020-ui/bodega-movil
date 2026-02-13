import streamlit as st
from supabase import create_client

# Conexión con las Llaves de la Corona
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.title("📦 Control de Inventario")

# Buscador manual (Mientras arreglamos el escáner)
codigo = st.text_input("Escribe o pega el código de barras aquí:")

if codigo:
    res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
    if res.data:
        prod = res.data[0]
        st.success(f"Producto: {prod['nombre']}")
        st.metric("Precio $", f"{prod['precio_dol']}")
    else:
        st.warning("Producto no encontrado.")

st.info("Nota: El escáner de cámara está desactivado temporalmente para mantener la estabilidad del servidor.")
