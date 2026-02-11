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

# 4. ESTILOS CSS (SIN FONDO, MÁXIMA CLARIDAD)
st.markdown(f"""
    <style>
    /* Fondo limpio para que no tape las letras */
    .stApp {{
        background-color: #FFFFFF;
    }}
    /* Contenedor del logo de arriba */
    .main-logo {{
        display: flex;
        justify-content: center;
        padding: 10px 0px;
        margin-bottom: 5px;
    }}
    /* Botones estilo profesional */
    .stButton>button {{ 
        width: 100%; 
        border-radius: 12px; 
        font-weight: bold; 
        background-color: #1f538d; 
        color: white; 
        height: 3.5em;
    }}
    /* Mejorar lectura de tablas en móvil */
    [data-testid="stTable"] {{
        font-size: 14px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGO EN EL ENCABEZADO ---
st.markdown(f'<div class="main-logo"><img src="{logo_url}" width="180"></div>', unsafe_allow_html=True)

# 5. LÓGICA DE TASA
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_v = 40.0

pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[0]:
    st.metric("Tasa Actual en Sistema", f"Bs. {tasa_v:,.2f}")
    nueva_tasa = st.number_input("Actualizar Tasa", value=tasa_v, step=0.01)
    if st.button("✅ GUARDAR TASA"):
        supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
        st.success("Tasa actualizada con éxito")
        st.rerun()

with pestanas[1]:
    busq = st.text_input("🔍 Buscar producto...").upper()
    res_p = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
    df = pd.DataFrame(res_p.data)
    
    if not df.empty:
        # Renombrar columnas para que se vean mejor en el celular
        df.columns = ["PRODUCTO", "USD $", "BS. TASA"]
        if busq:
            df = df[df['PRODUCTO'].str.contains(busq, na=False)]
        
        # Mostrar tabla ajustada al ancho del teléfono
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay productos cargados.")

with pestanas[2]:
    st.subheader("Nuevo Usuario")
    with st.form("new_user"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("👤 CREAR USUARIO"):
            if u and p:
                supabase.table("usuarios").insert({"usuario": u.lower(), "clave": p, "rol": "Operador"}).execute()
                st.success("¡Usuario creado!")
