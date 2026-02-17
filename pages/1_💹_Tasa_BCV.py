import streamlit as st
from config import conectar

supabase = conectar()
st.title("💹 Ajustar Tasa del Día")

# Leer tasa actual de la tabla 'ajustes'
res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_actual = float(res.data[0]['valor']) if res.data else 40.0

st.metric("Tasa en Sistema", f"{tasa_actual} Bs/$")

nueva_tasa = st.number_input("Nueva Tasa BCV:", value=tasa_actual, format="%.2f")

if st.button("🚀 Actualizar para todo el negocio"):
    supabase.table("ajustes").update({"valor": nueva_tasa}).eq("id", 1).execute()
    st.success(f"✅ Tasa cambiada a {nueva_tasa}. ¡La PC ya tiene el cambio!")
    st.rerun()
