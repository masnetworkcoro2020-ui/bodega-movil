import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="BODEGA PRO V2 - MÓVIL", layout="centered")

# 2. CONEXIÓN (TU LLAVE MAESTRA)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 3. MARCA DE AGUA (ESTA LÍNEA ES LA MAGIA)
# Cambia 'TU_USUARIO' por tu nombre de usuario de GitHub real
user_github = "TU_USUARIO_DE_GITHUB" 
logo_url = f"https://raw.githubusercontent.com/{user_github}/bodega-movil/main/logo.png"

st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.94), rgba(255,255,255,0.94)), 
                          url("{logo_url}");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center 120px;
        background-size: 250px;
    }}
    .stButton>button {{ width: 100%; border-radius: 15px; font-weight: bold; height: 3.5em; background-color: #1f538d; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# 4. OBTENER TASA (ID: 1)
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_v = 40.0

st.title("🏪 BODEGA PRO MÓVIL")
pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[0]:
    st.metric("Tasa Actual", f"Bs. {tasa_v:,.2f}")
    nueva_tasa = st.number_input("Cambiar Tasa", value=tasa_v)
    if st.button("💾 ACTUALIZAR TASA"):
        supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
        st.success("Tasa guardada")
        st.rerun()

with pestanas[1]:
    busq = st.text_input("🔍 Buscar Producto...").upper()
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
        if st.form_submit_button("👤 CREAR"):
            supabase.table("usuarios").insert({"usuario": u.lower(), "clave": p, "rol": "Operador"}).execute()
            st.success("Usuario creado")
