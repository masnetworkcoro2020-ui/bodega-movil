import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="BODEGA PRO V2 - MÓVIL", layout="centered")

# 2. CONEXIÓN (TU LLAVE MAESTRA MANTENIDA)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 3. LÓGICA DEL LOGO (YA CONFIGURADO PARA TU USUARIO)
# Ruta directa al archivo que ya subiste
logo_url = "https://raw.githubusercontent.com/masnetworkcoro2020-ui/bodega-movil/main/logo.png"

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
    .stButton>button {{ 
        width: 100%; 
        border-radius: 15px; 
        font-weight: bold; 
        height: 3.5em; 
        background-color: #1f538d; 
        color: white; 
    }}
    [data-testid="stMetricValue"] {{ color: #1f538d; }}
    </style>
    """, unsafe_allow_html=True)

# 4. OBTENER TASA (ID: 1 COMO EN INVENTARIO.PY)
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_v = 40.0

st.title("🏪 BODEGA PRO MÓVIL")
pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[0]:
    st.subheader("Control de Tasa")
    st.metric("Tasa Actual en Sistema", f"Bs. {tasa_v:,.2f}")
    nueva_tasa = st.number_input("Nueva Tasa de Venta", value=tasa_v, step=0.01)
    if st.button("💾 ACTUALIZAR TASA"):
        supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
        st.success(f"Tasa actualizada a {nueva_tasa}")
        st.rerun()

with pestanas[1]:
    st.subheader("Gestión de Inventario")
    busq = st.text_input("🔍 Buscar por nombre...").upper()
    res_p = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
    df = pd.DataFrame(res_p.data)
    if not df.empty:
        if busq:
            df = df[df['nombre'].str.contains(busq, na=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay productos registrados.")

with pestanas[2]:
    st.subheader("Control de Personal")
    with st.form("new_user"):
        u_name = st.text_input("Usuario (Login)").lower().strip()
        u_pass = st.text_input("Contraseña", type="password")
        if st.form_submit_button("👤 CREAR USUARIO"):
            if u_name and u_pass:
                supabase.table("usuarios").insert({"usuario": u_name, "clave": u_pass, "rol": "Operador"}).execute()
                st.success(f"Usuario {u_name} registrado")
