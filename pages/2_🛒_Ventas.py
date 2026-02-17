import streamlit as st
from config import conectar
from datetime import datetime

supabase = conectar()

# Traer la tasa fresca
res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa = float(res_t.data[0]['valor']) if res_t.data else 40.0

st.title("🛒 Facturación Rápida")

cod = st.text_input("Escanear/Escribir Código:")

if cod:
    res = supabase.table("productos").select("*").eq("codigo", cod).execute()
    if res.data:
        p = res.data[0]
        st.subheader(p['nombre'])
        
        # Cálculo de venta basado en la tasa actual
        p_bs = float(p['venta_usd']) * tasa
        st.metric("Precio Final", f"{p_bs:.2f} Bs", f"{p['venta_usd']} $")
        
        cant = st.number_input("Cantidad", min_value=1, value=1)
        if st.button("💸 Registrar Venta"):
            # Insertar en la tabla 'ventas' (Asegúrate de tenerla en Supabase)
            supabase.table("ventas").insert({
                "producto": p['nombre'],
                "cantidad": cant,
                "total_usd": float(p['venta_usd']) * cant,
                "fecha": datetime.now().isoformat()
            }).execute()
            st.success("✅ Venta registrada con éxito")
    else:
        st.error("Producto no encontrado.")
