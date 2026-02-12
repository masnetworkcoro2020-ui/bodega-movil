import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image, ImageOps
import numpy as np

# --- INTENTO DE IMPORTACIÓN SEGURO (Para evitar el error rojo de la foto) ---
try:
    import cv2
except ImportError:
    cv2 = None

try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

# 1. CONEXIÓN (Tus credenciales originales de Supabase)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. CONFIGURACIÓN Y ESTILOS (Colores idénticos a tu versión de escritorio)
st.set_page_config(page_title="BODEGA MOVIL 360", layout="centered")
st.markdown("""
    <style>
    .stNumberInput input, .stTextInput input { height: 50px !important; font-size: 18px !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black; font-weight: bold; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta $")) input { background-color: #d6eaf8 !important; color: black; }
    .stButton>button { width: 100%; height: 60px !important; border-radius: 12px; font-weight: bold; font-size: 20px !important; }
    .user-card { background-color: #f8f9fa; padding: 12px; border-radius: 10px; border-left: 5px solid #1f538d; margin-bottom: 8px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEMA DE LOGIN (LA ALCABALA) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>🔐 ACCESO BODEGA 360</h2>", unsafe_allow_html=True)
    u_acc = st.text_input("Usuario:")
    p_acc = st.text_input("Contraseña:", type="password")
    if st.button("INGRESAR AL SISTEMA"):
        res_auth = supabase.table("usuarios").select("*").eq("usuario", u_acc).eq("clave", p_acc).execute()
        if res_auth.data:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Usuario o Clave incorrectos, mano.")
    st.stop()

# --- 4. SI PASA EL LOGIN, CARGA TODO EL MOTOR ---

# OBTENCIÓN DE TASA (ID:1)
try:
    res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0
except Exception as e:
    tasa_v = 40.0

# Botón de salir
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

tab1, tab2, tab3 = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

# --- PESTAÑA 1: TASA ---
with tab1:
    st.subheader("Ajuste de Tasa Diaria")
    st.info(f"Tasa actual en sistema: {tasa_v} Bs/$")
    nt = st.number_input("Nueva Tasa:", value=tasa_v, format="%.2f")
    if st.button("💾 ACTUALIZAR TASA GLOBAL"):
        supabase.table("ajustes").update({"valor": nt}).eq("id", 1).execute()
        st.success("Tasa actualizada.")
        st.rerun()

# --- PESTAÑA 2: INVENTARIO (MOTOR 360 COMPLETO) ---
with tab2:
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
    
    # MÓDULO DE CÁMARA MEJORADO PARA ESCANEO
    foto_captura = st.camera_input("📷 ESCANEAR CÓDIGO (APUNTE Y DISPARE)")
    
    if foto_captura:
        img_pil = Image.open(foto_captura)
        
        # PROCESAMIENTO PARA QUE LEA MEJOR (Blanco y Negro)
        gray_img = ImageOps.grayscale(img_pil)
        img_array = np.array(gray_img)

        # Intentamos leer con pyzbar si está disponible
        if pyzbar:
            decoded_objs = pyzbar.decode(img_array)
            if not decoded_objs and cv2 is not None:
                # Si falla, aplicamos un filtro de contraste (Threshold)
                _, thr = cv2.threshold(img_array, 127, 255, cv2.THRESH_BINARY)
                decoded_objs = pyzbar.decode(thr)
            
            if decoded_objs:
                codigo_leido = decoded_objs[0].data.decode('utf-8')
                if codigo_leido != st.session_state.f["cod"]:
                    st.session_state.f["cod"] = codigo_leido
                    st.success(f"✅ ¡Código detectado!: {codigo_leido}")
                    st.rerun()
            else:
                st.warning("No se pudo leer el código. Intenta con más luz o acercando más el teléfono.")
        else:
            st.error("Librería de escaneo no disponible en el servidor. Ingrese el código manual.")

    # BUSCADOR DINÁMICO
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    opciones = ["-- NUEVO PRODUCTO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    seleccion = st.selectbox("🔍 Buscar producto para editar:", opciones)

    if seleccion != "-- NUEVO PRODUCTO --" and seleccion != st.session_state.get("last_sel"):
        p = df_lista[df_lista['nombre'] == seleccion].iloc[0]
        st.session_state.f = {
            "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
            "mar": float(p['margen']), "vbs": float(p['venta_bs']),
            "vusd": float(p['venta_usd']), "cod": str(p['codigo']), "nom": str(p['nombre'])
        }
        st.session_state.last_sel = seleccion
    elif seleccion == "-- NUEVO PRODUCTO --" and st.session_state.get("last_sel") != "-- NUEVO PRODUCTO --":
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
        st.session_state.last_sel = "-- NUEVO PRODUCTO --"

    # CAMPOS DE DATOS (Nombres idénticos a tu inventario.py)
    cod_in = st.text_input("Código de Barras:", value=st.session_state.f["cod"])
    nom_in = st.text_input("Nombre del Producto:", value=st.session_state.f["nom"])
    
    col_c1, col_c2 = st.columns(2)
    in_cbs = col_c1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = col_c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    
    in_mar = st.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    
    col_v1, col_v2 = st.columns(2)
    in_vusd = col_v1.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = col_v2.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # --- MOTOR 360° TOTAL (IGUAL A TU CLASE ModuloInventario) ---
    factor = (1 + (in_mar / 100))

    if in_cbs != st.session_state.f["cbs"]:
        st.session_state.f.update({"cbs": in_cbs, "cusd": in_cbs/tasa_v, "vusd": (in_cbs/tasa_v)*factor, "vbs": (in_cbs/tasa_v)*factor*tasa_v})
        st.rerun()
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f.update({"cusd": in_cusd, "cbs": in_cusd*tasa_v, "vusd": in_cusd*factor, "vbs": in_cusd*factor*tasa_v})
        st.rerun()
    elif in_mar != st.session_state.f["mar"]:
        st.session_state.f.update({"mar": in_mar, "vusd": st.session_state.f["cusd"]*factor, "vbs": st.session_state.f["cusd"]*factor*tasa_v})
        st.rerun()
    elif in_vbs != st.session_state.f["vbs"]:
        st.session_state.f.update({"vbs": in_vbs, "vusd": in_vbs/tasa_v, "cusd": (in_vbs/tasa_v)/factor, "cbs": ((in_vbs/tasa_v)/factor)*tasa_v})
        st.rerun()
    elif in_vusd != st.session_state.f["vusd"]:
        st.session_state.f.update({"vusd": in_vusd, "vbs": in_vusd*tasa_v, "cusd": in_vusd/factor, "cbs": (in_vusd/factor)*tasa_v})
        st.rerun()

    if st.button("💾 GUARDAR / ACTUALIZAR EN NUBE"):
        datos = {
            "codigo": cod_in.upper(), "nombre": nom_in.upper(),
            "costo_bs": st.session_state.f["cbs"], "costo_usd": st.session_state.f["cusd"],
            "margen": st.session_state.f["mar"], "venta_usd": st.session_state.f["vusd"], "venta_bs": st.session_state.f["vbs"]
        }
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Producto sincronizado!")
        st.rerun()

    if st.button("🗑️ ELIMINAR PRODUCTO", type="secondary"):
        supabase.table("productos").delete().eq("codigo", cod_in).execute()
        st.rerun()

    st.divider()
    if not df_lista.empty:
        st.dataframe(df_lista[["codigo", "nombre", "venta_bs", "costo_usd"]], use_container_width=True, hide_index=True)

# --- PESTAÑA 3: USUARIOS ---
with tab3:
    st.subheader("👥 Gestión de Accesos")
    res_u = supabase.table("usuarios").select("*").execute()
    for usr in res_u.data:
        st.markdown(f'<div class="user-card"><b>👤 {usr["usuario"]}</b></div>', unsafe_allow_html=True)
