import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="BODEGA PRO V2", layout="centered")

# 2. CONEXIÓN (TU LLAVE MAESTRA)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 3. RUTA DEL LOGO (TU GITHUB)
logo_url = "https://raw.githubusercontent.com/masnetworkcoro2020-ui/bodega-movil/main/logo.png"

# 4. ESTILOS CSS (LOGOS Y BOTONES)
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)), 
                          url("{logo_url}");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center center;
        background-size: 300px;
    }}
    .main-logo {{
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }}
    .stButton>button {{ 
        width: 100%; 
        border-radius: 15px; 
        font-weight: bold; 
        background-color: #1f538d; 
        color: white; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO CENTRADO ---
st.markdown(f'<div class="main-logo"><img src="{logo_url}" width="200"></div>', unsafe_allow_html=True)

# 5. LÓGICA DE TASA
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_v = 40.0

pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[0]:
    st.metric("Tasa Actual", f"Bs. {tasa_v:,.2f}")
    nueva_tasa = st.number_input("Nueva Tasa", value=tasa_v, step=0.1)
    if st.button("💾 ACTUALIZAR"):
        supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
        st.success("¡Tasa al día!")
        st.rerun()

with pestanas[1]:
    busq = st.text_input("🔍 Buscar...").upper()
    res_p = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
    df = pd.DataFrame(res_p.data)
    if not df.empty:
        if busq:
            df = df[df['nombre'].str.contains(busq, na=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)

with pestanas[2]:
    with st.form("new_user"):
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.form_submit_button("➕ CREAR"):
            if u and p:
                supabase.table("usuarios").insert({"usuario": u.lower(), "clave": p, "rol": "Operador"}).execute()
                st.success("Usuario agregado")
