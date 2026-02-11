import streamlit as st
from supabase import create_client
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Mi Bodega Pro", page_icon="🏪")

# Conexión con Supabase (usando tus datos de config.py)
try:
    from config import SUPABASE_URL, SUPABASE_KEY
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Error en configuración. Revisa config.py")

st.title("🏪 Mi Bodega Pro")

# Obtener tasa del BCV (Simulada o desde tu tabla si la tienes)
st.metric("Tasa BCV Actual", "Bs. 385.20") 

# Buscador
busqueda = st.text_input("🔍 Buscar producto por nombre...", "")

# Leer datos de tu tabla 'productos'
try:
    # Ajustado a tus nombres reales: nombre, venta_usd, venta_bs
    response = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Filtrar por búsqueda
        if busqueda:
            df = df[df['nombre'].str.contains(busqueda, case=False)]

        # Mostrar productos
        for index, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{row['nombre']}**")
                    st.caption("Disponible en tienda")
                with col2:
                    st.markdown(f"**${row['venta_usd']}**")
                    st.caption(f"Bs. {row['venta_bs']}")
                st.divider()
    else:
        st.warning("No hay productos registrados.")

except Exception as e:
    st.error(f"Error al conectar: {e}")
