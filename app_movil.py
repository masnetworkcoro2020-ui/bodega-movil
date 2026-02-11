import streamlit as st
from supabase import create_client
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Mi Bodega Pro", page_icon="🏪")

# DATOS OFICIALES DE TU CONFIG.PY
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

# Conexión directa
try:
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error(f"Error de conexión: {e}")

st.title("🏪 Mi Bodega Pro")
st.metric("Tasa BCV Actual", "Bs. 388.73") 

# Buscador
busqueda = st.text_input("🔍 Buscar producto...", "")

try:
    # Usando tus columnas reales: nombre, venta_usd, venta_bs
    response = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Filtro de búsqueda
        if busqueda:
            df = df[df['nombre'].str.contains(busqueda, case=False)]

        # Lista de productos
        for index, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{row['nombre']}**")
                    st.caption("Disponible")
                with col2:
                    st.markdown(f"**${row['venta_usd']}**")
                    st.caption(f"Bs. {row['venta_bs']}")
                st.divider()
    else:
        st.warning("No se encontraron productos.")
        
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
