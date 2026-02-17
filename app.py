import streamlit as st
from config import conectar
import pandas as pd

# Configuración de página móvil
st.set_page_config(page_title="Bodega Móvil", page_icon="🛒")

supabase = conectar()

st.title("📱 Bodega Pro Móvil")

# Menú sencillo para el pulgar
menu = ["Vender", "Inventario", "Tasa BCV"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Vender":
    st.header("🛒 Nueva Venta")
    # Componente de cámara nativo de Streamlit
    img_file = st.camera_input("Escanea el código de barras")
    
    if img_file:
        st.success("Imagen capturada. Procesando...")
        # Aquí conectaremos la lógica de búsqueda en Supabase

elif choice == "Inventario":
    st.header("📦 Stock Actual")
    res = supabase.table("productos").select("*").execute()
    df = pd.DataFrame(res.data)
    st.dataframe(df)

elif choice == "Tasa BCV":
    st.header("🪙 Tasa del Día")
    res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa = res.data[0]['valor'] if res.data else "No definida"
    st.metric("Tasa Actual", f"{tasa} Bs")
