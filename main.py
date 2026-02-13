import streamlit as st
from supabase import create_client
from camera_input_live import camera_input_live
from pyzbar import pyzbar
from PIL import Image

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Bodega Móvil", layout="centered")

URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# ADN de Navegación (Sustituye a las carpetas)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'pagina' not in st.session_state: st.session_state.pagina = "login"

# --- VISTA: LOGIN ---
if not st.session_state.auth:
    st.title("🔐 Acceso Administrativo")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR"):
        if u == "jmaar" and p == "15311751": #
            st.session_state.auth = True
            st.session_state.pagina = "panel"
            st.rerun()
    st.stop()

# --- VISTA: PANEL (Imagen 2 corregida) ---
if st.session_state.pagina == "panel":
    st.title("🕹️ Panel de Control")
    st.write("Bienvenido, **JMAAR**")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 ABRIR INVENTARIO", use_container_width=True):
            st.session_state.pagina = "inventario"
            st.rerun()
    with col2:
        if st.button("🪙 TASA BCV", use_container_width=True):
            st.session_state.pagina = "tasa"
            st.rerun()

# --- VISTA: INVENTARIO (Tu lógica de protección) ---
elif st.session_state.pagina == "inventario":
    st.title("📦 Inventario")
    if st.button("⬅️ VOLVER AL PANEL"):
        st.session_state.pagina = "panel"
        st.rerun()

    # Obtener tasa desde tabla ajustes ID:1
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

    st.subheader("📷 Escáner")
    img_file = camera_input_live()
    codigo_cam = ""
    if img_file:
        decoded = pyzbar.decode(Image.open(img_file))
        if decoded:
            codigo_cam = decoded[0].data.decode('utf-8')
            st.success(f"Código: {codigo_cam}")

    cod = st.text_input("Código de barras:", value=codigo_cam)
    if cod:
        res = supabase.table("productos").select("*").eq("codigo", cod).execute()
        if res.data:
            p = res.data[0]
            # TU LÓGICA 360: Costo USD -> Margen 25% -> Precio Bs
            c_usd = float(p.get('costo_usd', 0))
            margen = float(p.get('margen', 25))
            v_usd = c_usd * (1 + (margen/100))
            v_bs = v_usd * tasa
            
            st.success(f"PRODUCTO: {p['nombre']}")
            st.metric("PRECIO FINAL BS", f"{v_bs:.2f} Bs")
            st.write(f"Ref: {v_usd:.2f} $ | Tasa: {tasa}")
        else:
            st.error("No registrado.")

# --- VISTA: TASA BCV ---
elif st.session_state.pagina == "tasa":
    st.title("🪙 Tasa BCV")
    if st.button("⬅️ VOLVER"):
        st.session_state.pagina = "panel"
        st.rerun()
    
    res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    actual = res.data[0]['valor'] if res.data else "40.0"
    
    st.metric("Tasa Actual", f"{actual} Bs.")
    nueva = st.text_input("Nueva Tasa:", value=actual)
    if st.button("ACTUALIZAR"):
        supabase.table("ajustes").update({"valor": nueva}).eq("id", 1).execute()
        st.success("Tasa guardada.")
        st.rerun()
