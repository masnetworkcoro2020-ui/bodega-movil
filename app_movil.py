import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Mismas credenciales)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS DE COLORES (Tu código original de PC)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; background-color: #1f538d; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ACTUAL ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑAS ---
pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[1]:
    st.subheader("🛠️ Gestión 360°")
    
    # Quitamos el selectbox de selección manual y dejamos el flujo libre
    st.camera_input("📷 ESCANEAR")
    
    with st.container():
        # Ahora los campos están vacíos listos para recibir datos del escáner o teclado
        cod = st.text_input("Código")
        nom = st.text_input("Producto")
        
        c_bs = st.number_input("Costo Bs. (Fijo)", value=0.0, format="%.2f")
        c_usd = st.number_input("Costo $", value=0.0, format="%.2f")
        
        # Lógica de ajuste 360°
        modo = st.radio("¿Cómo quieres ajustar?", ["Por Margen %", "Por Precio Bs."], horizontal=True)
        
        if modo == "Por Margen %":
            m_input = st.number_input("Margen %", value=25.0)
            v_usd = c_usd * (1 + (m_input/100))
            v_bs = v_usd * tasa_v
            st.number_input("Venta Bs. (Resultado)", value=v_bs, disabled=True)
        else:
            v_bs = st.number_input("Venta Bs. (Manual)", value=0.0)
            v_usd = v_bs / tasa_v if tasa_v > 0 else 0
            m_input = ((v_usd / c_usd) - 1) * 100 if c_usd > 0 else 0
            st.write(f"📈 Nuevo Margen calculado: **{m_input:.2f}%**")
            st.write(f"💵 Venta en $: **{v_usd:.2f}**")

        if st.button("💾 GUARDAR CAMBIOS"):
            datos = {
                "codigo": cod.upper(), 
                "nombre": nom.upper(),
                "costo_bs": c_bs, 
                "costo_usd": c_usd,
                "margen": round(m_input, 2), 
                "venta_usd": round(v_usd, 2), 
                "venta_bs": round(v_bs, 2)
            }
            # Upsert para que si el código ya existe, lo actualice (como en tu PC)
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Sincronizado con éxito!")
            st.rerun()

    st.divider()
    st.subheader("📋 Inventario Registrado")
    # Cargamos la lista completa para consulta rápida abajo
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    st.dataframe(df[["nombre", "venta_usd", "venta_bs"]], use_container_width=True, hide_index=True)
