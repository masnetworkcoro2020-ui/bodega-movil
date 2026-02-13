import streamlit as st
from supabase import create_client
from camera_input_live import camera_input_live
from pyzbar import pyzbar
from PIL import Image

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Bodega Móvil", layout="centered")

# Credenciales (Asegúrate de que sean las correctas)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Tu clave completa
supabase = create_client(URL, KEY)

# Inicialización del Estado de la Sesión
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"

# --- LÓGICA DE NAVEGACIÓN (EL PORTERO) ---

# SI NO ESTÁ AUTENTICADO: Solo muestra Login
if not st.session_state.auth:
    st.title("🔐 Acceso Administrativo")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Contraseña", type="password")
    
    if st.button("INGRESAR"):
        # Verifica credenciales
        if u == "jmaar" and p == "15311751":
            st.session_state.auth = True
            st.session_state.pagina = "panel"
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    # Importante: No dejar que pase de aquí si no está autenticado
    st.stop()

# --- SI LLEGA AQUÍ, ES PORQUE YA PASÓ AL PORTERO ---

# --- VISTA: PANEL ---
if st.session_state.pagina == "panel":
    st.title("🕹️ Panel de Control")
    st.write(f"Bienvenido, **JMAAR**")
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
    
    if st.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

# --- VISTA: INVENTARIO ---
elif st.session_state.pagina == "inventario":
    st.title("📦 Inventario")
    if st.button("⬅️ VOLVER AL PANEL"):
        st.session_state.pagina = "panel"
        st.rerun()

    # Obtener tasa con seguridad
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

    st.subheader("📷 Escáner")
    img_file = camera_input_live()
    codigo_cam = ""
    
    if img_file:
        img = Image.open(img_file)
        decoded = pyzbar.decode(img)
        if decoded:
            codigo_cam = decoded[0].data.decode('utf-8')
            st.success(f"Código detectado: {codigo_cam}")

    cod = st.text_input("Código de barras:", value=codigo_cam)
    
    if cod:
        res = supabase.table("productos").select("*").eq("codigo", cod).execute()
        if res.data:
            p = res.data[0]
            # Lógica de precios
            c_usd = float(p.get('costo_usd', 0))
            margen = float(p.get('margen', 25))
            v_usd = c_usd * (1 + (margen/100))
            v_bs = v_usd * tasa
            
            st.success(f"PRODUCTO: {p['nombre']}")
            st.metric("PRECIO FINAL BS", f"{v_bs:.2f} Bs")
            st.info(f"Ref: {v_usd:.2f} $ | Tasa: {tasa}")
        else:
            st.error("Producto no registrado en la base de datos.")

# --- VISTA: TASA BCV ---
elif st.session_state.pagina == "tasa":
    st.title("🪙 Tasa BCV")
    if st.button("⬅️ VOLVER"):
        st.session_state.pagina = "panel"
        st.rerun()
    
    res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    actual = res.data[0]['valor'] if res.data else "40.0"
    
    st.metric("Tasa Actual", f"{actual} Bs.")
    nueva = st.text_input("Nueva Tasa:", value=str(actual))
    
    if st.button("ACTUALIZAR"):
        try:
            supabase.table("ajustes").update({"valor": nueva}).eq("id", 1).execute()
            st.success("Tasa actualizada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al actualizar: {e}")
