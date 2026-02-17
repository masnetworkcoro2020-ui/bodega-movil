import streamlit as st
from config import conectar
import pandas as pd

supabase = conectar()
st.title("📋 Reporte de Ventas")

res = supabase.table("ventas").select("*").order("id", desc=True).limit(50).execute()

if res.data:
    df = pd.DataFrame(res.data)
    st.dataframe(df[['fecha', 'producto', 'cantidad', 'total_usd']], use_container_width=True)
else:
    st.info("No hay ventas registradas aún.")
