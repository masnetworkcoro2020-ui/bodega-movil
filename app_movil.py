import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image, ImageOps
import numpy as np
import cv2  # Usamos OpenCV como en tu inventario.py

# Intentamos importar pyzbar
try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

# 1. CONEXIÓN (Tus credenciales reales)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. CONFIGURACIÓN Y ESTILOS
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

# --- 3. LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 ACCESO BODEGA 360")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("ENTRAR"):
        res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
        if res.data:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error("Error de acceso")
    st.stop()

# --- 4. MOTOR DE INVENTARIO ---
try:
    res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0
except: tasa_v = 40.0

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

tab1, tab2, tab3 = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with tab1:
    st.subheader("Tasa del día")
    nt = st.number_input("Tasa:", value=tasa_v)
    if st.button("ACTUALIZAR"):
        supabase.table("ajustes").update({"valor": nt}).eq("id", 1).execute()
        st.rerun()

with tab2:
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

    # --- ESCÁNER MEJORADO ---
    foto = st.camera_input("📷 ESCANEAR CÓDIGO")
    
    if foto:
        # Procesamiento de imagen (como en tu versión de escritorio)
        img = Image.open(foto)
        # 1. Convertir a escala de grises para mejor lectura
        gray_img = ImageOps.grayscale(img)
        img_np = np.array(gray_img)
        
        # 2. Intentar decodificar
        decoded = pyzbar.decode(img_np)
        
        # 3. Si falla, intentar mejorar el contraste (Thresholding)
        if not decoded:
            _, thr = cv2.threshold(img_np, 127, 255, cv2.THRESH_BINARY)
            decoded = pyzbar.decode(thr)
            
        if decoded:
            codigo = decoded[0].data.decode('utf-8')
            st.session_state.f["cod"] = codigo
            st.success(f"¡Código Detectado!: {codigo}")
            # Buscamos si ya existe
            res_busq = supabase.table("productos").select("*").eq("codigo", codigo).execute()
            if res_busq.data:
                p = res_busq.data[0]
                st.session_state.f.update({
                    "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
                    "mar": float(p['margen']), "vbs": float(p['venta_bs']),
                    "vusd": float(p['venta_usd']), "nom": p['nombre']
                })
            st.rerun()
        else:
            st.warning("⚠️ No se leyó bien. Asegúrate de que el código esté centrado y no brille.")

    # BUSCADOR
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    opciones = ["-- NUEVO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    sel = st.selectbox("🔍 Buscar:", opciones)

    if sel != "-- NUEVO --" and sel != st.session_state.get("last_s"):
        p = df_lista[df_lista['nombre'] == sel].iloc[0]
        st.session_state.f.update({
            "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
            "mar": float(p['margen']), "vbs": float(p['venta_bs']),
            "vusd": float(p['venta_usd']), "cod": str(p['codigo']), "nom": str(p['nombre'])
        })
        st.session_state.last_s = sel

    # CAMPOS (Lógica de 195 líneas)
    c1 = st.text_input("Código:", value=st.session_state.f["cod"])
    n1 = st.text_input("Producto:", value=st.session_state.f["nom"])
    
    col1, col2 = st.columns(2)
    in_cbs = col1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = col2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    in_mar = st.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    
    col3, col4 = st.columns(2)
    in_vusd = col3.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = col4.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # --- MOTOR 360 (IGUAL A INVENTARIO.PY) ---
    factor = (1 + (in_mar / 100))
    if in_cbs != st.session_state.f["cbs"]:
        st.session_state.f.update({"cbs": in_cbs, "cusd": in_cbs/tasa_v, "vusd": (in_cbs/tasa_v)*factor, "vbs": (in_cbs/tasa_v)*factor*tasa_v})
        st.rerun()
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f.update({"cusd": in_cusd, "cbs": in_cusd*tasa_v, "vusd": in_cusd*factor, "vbs": in_cusd*factor*tasa_v})
        st.rerun()
    elif in_vbs != st.session_state.f["vbs"]:
        st.session_state.f.update({"vbs": in_vbs, "vusd": in_vbs/tasa_v, "cusd": (in_vbs/tasa_v)/factor, "cbs": ((in_vbs/tasa_v)/factor)*tasa_v})
        st.rerun()

    if st.button("💾 GUARDAR"):
        d = {"codigo": c1, "nombre": n1.upper(), "costo_bs": st.session_state.f["cbs"], "costo_usd": st.session_state.f["cusd"], "margen": st.session_state.f["mar"], "venta_usd": st.session_state.f["vusd"], "venta_bs": st.session_state.f["vbs"]}
        supabase.table("productos").upsert(d).execute()
        st.success("Guardado!")
        st.rerun()

with tab3:
    st.subheader("Usuarios")
    u_list = supabase.table("usuarios").select("*").execute()
    for usr in u_list.data:
        st.markdown(f'<div class="user-card">👤 {usr["usuario"]}</div>', unsafe_allow_html=True)
