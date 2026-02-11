import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="BODEGA PRO V2 - SEGURIDAD", layout="centered")

# 2. CONEXIÓN (TU LLAVE MAESTRA)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 3. RUTA DEL LOGO (MANTENEMOS EL DE GITHUB)
logo_url = "https://raw.githubusercontent.com/masnetworkcoro2020-ui/bodega-movil/main/logo.png"

# 4. ESTILOS CSS (FONDO LIMPIO PARA MÓVIL)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    .main-logo {{ display: flex; justify-content: center; padding: 10px; }}
    .stButton>button {{ width: 100%; border-radius: 12px; font-weight: bold; background-color: #1f538d; color: white; height: 3.5em; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE LOGIN INTELIGENTE ---
def login():
    st.markdown(f'<div class="main-logo"><img src="{logo_url}" width="150"></div>', unsafe_allow_html=True)
    st.subheader("🔐 Acceso de Seguridad")
    
    with st.form("login_form"):
        user_input = st.text_input("Usuario").lower().strip()
        pass_input = st.text_input("Contraseña", type="password")
        btn = st.form_submit_button("INGRESAR")
        
        if btn:
            # 1. LLAVE MAESTRA DE EMERGENCIA
            if user_input == "admin" and pass_input == "12345":
                st.session_state["autenticado"] = True
                st.rerun()
            
            # 2. BÚSQUEDA EN TU TABLA DE USUARIOS
            else:
                try:
                    res = supabase.table("usuarios").select("*").eq("usuario", user_input).eq("clave", pass_input).execute()
                    
                    if res.data:
                        # Sacamos el rol y lo pasamos a minúsculas para que no falle
                        rol_usuario = str(res.data[0].get("rol", "")).lower()
                        
                        # Aceptamos maestro, administrador o admin
                        if rol_usuario in ["maestro", "administrador", "admin"]:
                            st.session_state["autenticado"] = True
                            st.rerun()
                        else:
                            st.error(f"El rol '{rol_usuario}' no tiene permiso de acceso.")
                    else:
                        st.error("Usuario o contraseña incorrectos.")
                except Exception as e:
                    st.error("Error de conexión con la base de datos.")

# --- CONTROL DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    login()
else:
    # --- INTERFAZ DEL SISTEMA CUANDO YA ENTRASTE ---
    st.markdown(f'<div class="main-logo"><img src="{logo_url}" width="120"></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        if st.button("🚪 Cerrar Sesión"):
            st.session_state["autenticado"] = False
            st.rerun()

    # Lógica de la Tasa
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
    except:
        tasa_v = 40.0

    pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

    with pestanas[0]:
        st.metric("Tasa Actual", f"Bs. {tasa_v:,.2f}")
        nueva_tasa = st.number_input("Cambiar Tasa", value=tasa_v, step=0.01)
        if st.button("✅ ACTUALIZAR TASA"):
            supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
            st.success("Tasa guardada en la nube.")
            st.rerun()

    with pestanas[1]:
        busq = st.text_input("🔍 Buscar...").upper()
        res_p = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
        df = pd.DataFrame(res_p.data)
        if not df.empty:
            df.columns = ["PRODUCTO", "USD $", "BS. TASA"]
            if busq:
                df = df[df['PRODUCTO'].str.contains(busq, na=False)]
            st.dataframe(df, use_container_width=True, hide_index=True)

    with pestanas[2]:
        st.subheader("Usuarios Registrados")
        # Mostrar la lista actual de tu captura
        res_u = supabase.table("usuarios").select("usuario, rol").execute()
        st.table(pd.DataFrame(res_u.data))
