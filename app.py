import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración
st.set_page_config(page_title="Royal Essence Móvil", layout="centered")
supabase = conectar()

if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Royal Essence - Bodega")

menu = ["📸 Escáner", "🛒 Ventas", "📦 Inventario Completo"]
opcion = st.sidebar.radio("Menú:", menu)

# --- MÉDULA: ESCÁNER ---
if opcion == "📸 Escáner":
    st.subheader("Paso 1: Escanear Código")
    foto = st.camera_input("Enfoca el producto")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            lectura = codigos[0].data.decode('utf-8').strip()
            # Limpieza para códigos de 12 dígitos
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Detectado: {st.session_state.codigo_escaneado}")
        else:
            st.warning("No se leyó nada.")

# --- MÉDULA: VENTAS ---
elif opcion == "🛒 Ventas":
    st.subheader("Consulta de Precio")
    cod_actual = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        if res.data:
            p = res.data[0]
            st.markdown(f"### ✨ {p.get('nombre', 'Sin nombre')}")
            st.metric("Precio USD", f"$ {p.get('venta_usd', 0)}")
            st.write(f"**Precio Bs:** {p.get('venta_bs', 0)} Bs")
            
            # Solo muestra existencia si ya creaste la columna
            if 'existencia' in p:
                st.metric("Stock", f"{p['existencia']} und")
            else:
                st.warning("⚠️ Nota: Columna 'existencia' no encontrada en Supabase.")
        else:
            st.error("Producto no encontrado.")

# --- MÉDULA: INVENTARIO ---
elif opcion == "📦 Inventario Completo":
    st.subheader("Lista de Productos")
    try:
        # Solo pedimos las columnas que veo en tu foto
        res = supabase.table("productos").select("codigo, nombre, venta_usd, venta_bs").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
