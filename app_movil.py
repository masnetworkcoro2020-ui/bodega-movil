import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="BODEGA PRO V2 - MÓVIL", layout="centered")

# 2. CONEXIÓN (TU LLAVE MAESTRA)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 3. LÓGICA DEL LOGO AUTOMÁTICO
# --- REEMPLAZA SOLO ESTO ---
mi_usuario_github = "TU_USUARIO_AQUI" 
# ---------------------------

logo_url = f"https://raw.githubusercontent.com/{mi_usuario_github}/bodega-movil/main/logo.png"

st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.92)), 
                          url("{logo_url}");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center 150px;
        background-size: 280px;
    }}
    .stButton>button {{ 
        width: 100%; 
        border-radius: 20px; 
        font-weight: bold; 
        height: 3.8em; 
        background-color: #1f538d; 
        color: white;
        border: 2px solid #FFD700;
    }}
    [data-testid="stMetricValue"] {{ color: #1f538d; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 4. OBTENER TASA (COMO EN TU INVENTARIO.PY)
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_v = 40.0

st.title("🏪 BODEGA PRO MÓVIL")
pestanas = st.tabs(["💰 TASA BCV", "📦 INVENTARIO", "👥 USUARIOS"])

# --- PESTAÑA 1: TASA ---
with pestanas[0]:
    st.metric("Tasa Actual", f"Bs. {tasa_v:,.2f}")
    nueva_tasa = st.number_input("Nueva Tasa", value=tasa_v, step=0.01)
    if st.button("✅ ACTUALIZAR TASA"):
        supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
        st.success("¡Tasa actualizada en todo el sistema!")
        st.rerun()

# --- PESTAÑA 2: INVENTARIO ---
with pestanas[1]:
    busq = st.text_input("🔍 Buscar Producto...").upper()
    res_p = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
    df = pd.DataFrame(res_p.data)
    if not df.empty:
        if busq:
            df = df[df['nombre'].str.contains(busq, na=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- PESTAÑA 3: USUARIOS ---
with pestanas[2]:
    with st.form("new_user"):
        u = st.text_input("Nombre de Usuario").lower().strip()
        p = st.text_input("Clave de Acceso", type="password")
        if st.form_submit_button("👤 REGISTRAR TRABAJADOR"):
            if u and p:
                supabase.table("usuarios").insert({"usuario": u, "clave": p, "rol": "Operador"}).execute()
                st.success(f"Usuario {u} listo.")
