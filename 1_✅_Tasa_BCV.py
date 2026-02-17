import streamlit as st
from config import conectar

st.set_page_config(page_title="Tasa BCV", layout="centered")
supabase = conectar()

st.title("💵 Ajuste de Tasa BCV")

# Buscamos la tasa actual en la base de datos
res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_actual = float(res.data[0]['valor']) if res.data else 40.0

st.metric("Tasa Actual", f"{tasa_actual} Bs/$")

nueva_tasa = st.number_input("Nueva Tasa (Bs)", value=tasa_actual, step=0.1)

if st.button("Actualizar Tasa para todo el sistema"):
    supabase.table("ajustes").update({"valor": nueva_tasa}).eq("id", 1).execute()
    st.success(f"✅ Tasa actualizada a {nueva_tasa} Bs. ¡Ahora todo el inventario se recalculó!")
    st.balloons()
