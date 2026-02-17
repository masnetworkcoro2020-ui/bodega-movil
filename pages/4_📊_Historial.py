import streamlit as st
from config import conectar
import pandas as pd

st.set_page_config(page_title="Historial Lyan", layout="wide")
supabase = conectar()

st.title("📊 Historial de Ventas")

# Filtros rápidos en la barra lateral
st.sidebar.header("Filtros")
fecha_busqueda = st.sidebar.date_input("Ver ventas del día:")

# Traemos la data uniendo las tablas 'ventas' y 'productos'
# Nota: Usamos una consulta que trae el nombre del producto relacionado
res = supabase.table("ventas").select("fecha, monto_usd, monto_bs, metodo, productos(nombre)").order("fecha", desc=True).execute()

if res.data:
    # Aplanamos la data para que el nombre del producto se vea bien
    datos_limpios = []
    for v in res.data:
        datos_limpios.append({
            "Fecha": v['fecha'][:16].replace('T', ' '), # Limpiamos el formato de fecha
            "Producto": v['productos']['nombre'] if v['productos'] else "Desconocido",
            "Monto $": v['monto_usd'],
            "Monto Bs": v['monto_bs'],
            "Pago": v['metodo']
        })
    
    df = pd.DataFrame(datos_limpios)
    
    # --- RESUMEN DE CAJA ---
    col1, col2, col3 = st.columns(3)
    total_dolares = df["Monto $"].sum()
    total_bolivares = df["Monto Bs"].sum()
    
    col1.metric("Total en $", f"{total_dolares:.2f} $")
    col2.metric("Total en Bs", f"{total_bolivares:.2f} Bs")
    col3.metric("Nro. Ventas", len(df))

    st.divider()

    # --- TABLA DETALLADA ---
    st.write("### Detalle de Movimientos")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Gráfico rápido de métodos de pago
    if not df.empty:
        st.write("### 💳 Ventas por Método de Pago")
        resumen_pago = df.groupby("Pago")["Monto $"].sum()
        st.bar_chart(resumen_pago)

else:
    st.info("Aún no hay ventas registradas para mostrar.")
