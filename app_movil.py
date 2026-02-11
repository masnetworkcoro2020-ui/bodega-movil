import streamlit as st
from supabase import create_client
import pandas as pd

st.set_page_config(page_title="Mi Bodega Pro", page_icon="🏪")

# Conexión
try:
    from config import SUPABASE_URL, SUPABASE_KEY
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Error en configuración. Revisa config.py")

st.title("🏪 Mi Bodega Pro")
st.metric("Tasa BCV Actual", "Bs. 388.73") # Actualizada a tu última imagen

busqueda = st.text_input("🔍 Buscar producto...", "")

try:
    # Usando tus nombres reales de Supabase
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
    st.error(f"Error: {e}")
