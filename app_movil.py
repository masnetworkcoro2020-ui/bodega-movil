import streamlit as st
from supabase import create_client
import pandas as pd

st.set_page_config(page_title="Mi Bodega Pro", page_icon="🏪")

# Ponemos tus datos directo aquí para que no den error
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "TU_LLAVE_AQUI" # <--- MANO, PEGA AQUÍ TU LLAVE QUE ESTÁ EN CONFIG.PY

try:
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error(f"Error de conexión: {e}")

st.title("🏪 Mi Bodega Pro")
st.metric("Tasa BCV Actual", "Bs. 388.73") 

busqueda = st.text_input("🔍 Buscar producto...", "")

try:
    # Usando tus columnas: nombre, venta_usd, venta_bs
    response = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        if busqueda:
            df = df[df['nombre'].str.contains(busqueda, case=False)]

        for index, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{row['nombre']}**")
                with col2:
                    st.markdown(f"**${row['venta_usd']}**")
                    st.caption(f"Bs. {row['venta_bs']}")
                st.divider()
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
