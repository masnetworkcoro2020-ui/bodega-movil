import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image, ImageOps
import numpy as np

# Intentos de importación para que no explote la app
try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

try:
    import cv2
except ImportError:
    cv2 = None

# 1. CONEXIÓN (Tus credenciales reales)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS DE TU VERSIÓN DE ESCRITORIO
st.set_page_config(page_title="BODEGA MOVIL 360", layout="centered")
st.markdown("""
    <style>
    .stNumberInput input { height: 50px !important; font-size: 18px !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black; font-weight: bold; }
    .stButton>button { width: 100%; height: 60px !important; border-radius: 12px; font-weight: bold; font-size: 18px !important; }
    div[data-testid="stTextInput"]:has(label:contains("Código:")) input { border: 2px solid #2874A6 !important; font-weight: bold; color: #1B4F72; }
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
    st.stop()

# --- 4. MOTOR 360 ---
try:
    res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0
except: tasa_v = 40.0

if "f" not in st.session_state:
    st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

tab1, tab2, tab3 = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with tab2:
    # ESCÁNER REPOTENCIADO (CORREGIDO SIN CEROS EXTRAS)
    foto = st.camera_input("📷 ESCANEAR CÓDIGO")
    
    if foto:
        if pyzbar:
            img = Image.open(foto)
            img_np = np.array(ImageOps.grayscale(img))
            # Le pedimos a pyzbar que sea literal
            decoded = pyzbar.decode(img_np)
            
            if not decoded and cv2 is not None:
                _, thr = cv2.threshold(img_np, 127, 255, cv2.THRESH_BINARY)
                decoded = pyzbar.decode(thr)
            
            if decoded:
                # Aquí está el cambio: tomamos el valor crudo sin procesar nada más
                codigo_sucio = str(decoded[0].data.decode('utf-8'))
                codigo_final = codigo_sucio.strip() # Solo quita espacios si los hay, no agrega nada
                
                st.session_state.f["cod"] = codigo_final
                
                # Buscamos de una vez en Supabase
                res_b = supabase.table("productos").select("*").eq("codigo", codigo_final).execute()
                if res_b.data:
                    p = res_b.data[0]
                    st.session_state.f.update({
                        "nom": p['nombre'], "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
                        "mar": float(p['margen']), "vbs": float(p['venta_bs']), "vusd": float(p['venta_usd'])
                    })
                st.success(f"✅ ¡Leído con exactitud!: {codigo_final}")
                st.rerun()
            else:
                st.warning("No se leyó nada. Asegúrate de que el código no tenga reflejos.")
        else:
            st.error("Error de librerías en el servidor.")

    # BUSCADOR
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    opciones = ["-- NUEVO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    sel = st.selectbox("🔍 Buscar producto:", opciones)

    if sel != "-- NUEVO --" and sel != st.session_state.get("last_s"):
        p = df_lista[df_lista['nombre'] == sel].iloc[0]
        st.session_state.f.update({"cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']), "mar": float(p['margen']), "vbs": float(p['venta_bs']), "vusd": float(p['venta_usd']), "cod": str(p['codigo']), "nom": str(p['nombre'])})
        st.session_state.last_s = sel

    # FORMULARIO (MEMORIA DEL SISTEMA)
    cod_in = st.text_input("Código:", value=st.session_state.f["cod"])
    nom_in = st.text_input("Producto:", value=st.session_state.f["nom"])
    
    c1, c2 = st.columns(2)
    in_cbs = c1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    in_mar = st.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    
    c3, c4 = st.columns(2)
    in_vusd = c3.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = c4.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # RECALCULO MOTOR 360 (Igual a tu inventario.py)
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
        d = {"codigo": cod_in, "nombre": nom_in.upper(), "costo_bs": in_cbs, "costo_usd": in_cusd, "margen": in_mar, "venta_usd": in_vusd, "venta_bs": in_vbs}
        supabase.table("productos").upsert(d).execute()
        st.success("¡Producto Guardado!")
        st.rerun()

    if st.button("✨ LIMPIAR FORMULARIO"):
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
        st.rerun()

with tab1:
    st.subheader("Configuración de Tasa")
    nt = st.number_input("Tasa:", value=tasa_v)
    if st.button("ACTUALIZAR TASA"):
        supabase.table("ajustes").update({"valor": nt}).eq("id", 1).execute()
        st.rerun()
