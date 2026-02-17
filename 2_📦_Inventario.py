import streamlit as st
from config import conectar
import pandas as pd

st.set_page_config(page_title="Inventario - Lyan", layout="wide")
supabase = conectar()

st.title("📦 Inventario de Productos")

# Botón para refrescar manualmente por si acaso
if st.button("🔄 Sincronizar con la Nube"):
    st.rerun()

# Traemos la data de la tabla productos
res = supabase.table("productos").select("codigo, nombre, costo_usd, margen, venta_usd, venta_bs").execute()

if res.data:
    df = pd.DataFrame(res.data)
    # Renombramos las columnas para que se vea profesional
    df.columns = ["Código", "Producto", "Costo $", "Ganancia %", "Precio $", "Precio Bs"]
    
    # Buscador rápido por nombre o código
    busqueda = st.text_input("🔍 Buscar producto por nombre o código:")
    if busqueda:
        df = df[df['Producto'].str.contains(busqueda.upper()) | df['Código'].str.contains(busqueda)]

    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No hay productos registrados aún.")
