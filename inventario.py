import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import numpy as np

try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

# Intentamos importar cv2 para mejorar la imagen si pyzbar falla solo
try:
    import cv2
except ImportError:
    cv2 = None

def mostrar(supabase):
    # 1. OBTENER TASA (ID:1)
    try:
        res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0
    except: tasa_v = 40.0

    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

    # --- 2. ESCÁNER CON MEJORA DE IMAGEN ---
    foto = st.camera_input("📷 ESCANEAR CÓDIGO")
    
    if foto and pyzbar:
        img = Image.open(foto)
        # Convertimos a escala de grises para que pyzbar no se confunda con colores
        img_np = np.array(ImageOps.grayscale(img))
        
        # Intento 1: Lectura normal
        decoded = pyzbar.decode(img_np)
        
        # Intento 2: Si falla, aplicamos filtro de blanco y negro puro (Threshold)
        if not decoded and cv2 is not None:
            _, thr = cv2.threshold(img_np, 127, 255, cv2.THRESH_BINARY)
            decoded = pyzbar.decode(thr)

        if decoded:
            raw_code = str(decoded[0].data.decode('utf-8')).strip()
            # Regla de oro: quitar 0 inicial de UPC-A
            codigo_final = raw_code[1:] if raw_code.startswith('0') and len(raw_code) > 10 else raw_code
            
            st.session_state.f["cod"] = codigo_final
            
            # Busqueda automática en Supabase
            res_b = supabase.table("productos").select("*").eq("codigo", codigo_final).execute()
            if res_b.data:
                p = res_b.data[0]
                st.session_state.f.update({
                    "nom": p.get('nombre', ''), "cbs": float(p.get('costo_bs', 0)),
                    "cusd": float(p.get('costo_usd', 0)), "mar": float(p.get('margen', 25)),
                    "vbs": float(p.get('venta_bs', 0)), "vusd": float(p.get('venta_usd', 0))
                })
            st.rerun()
        else:
            st.warning("⚠️ No se detectó código. Intenta centrar las barras en el cuadro.")

    # --- 3. FORMULARIO 360 (Tus colores exactos) ---
    st.markdown("""
        <style>
        div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black; }
        div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    cod_in = st.text_input("Código:", value=st.session_state.f["cod"])
    nom_in = st.text_input("Producto:", value=st.session_state.f["nom"])

    col1, col2, col3 = st.columns(3)
    in_cbs = col1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = col2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    in_mar = col3.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")

    col4, col5 = st.columns(2)
    in_vusd = col4.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = col5.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # --- 4. LÓGICA DE RECALCULO (Motor 360) ---
    factor = (1 + (in_mar / 100))
    if in_cbs != st.session_state.f["cbs"]:
        st.session_state.f.update({"cbs": in_cbs, "cusd": in_cbs/tasa_v, "vusd": (in_cbs/tasa_v)*factor, "vbs": (in_cbs/tasa_v)*factor*tasa_v})
        st.rerun()
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f.update({"cusd": in_cusd, "cbs": in_cusd*tasa_v, "vusd": in_cusd*factor, "vbs": in_cusd*factor*tasa_v})
        st.rerun()

    # --- 5. GUARDAR ---
    if st.button("💾 GUARDAR / ACTUALIZAR", use_container_width=True):
        d = {"codigo": cod_in.upper(), "nombre": nom_in.upper(), "costo_bs": in_cbs, "costo_usd": in_cusd, "margen": in_mar, "venta_usd": in_vusd, "venta_bs": in_vbs}
        supabase.table("productos").upsert(d).execute()
        st.success("¡Guardado!")
