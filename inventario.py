import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np

# Intentamos importar pyzbar (asegúrate de que esté en requirements.txt)
try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

def mostrar(supabase):
    st.markdown("<h2 style='text-align: center;'>📦 INVENTARIO (REPOSICIÓN 360)</h2>", unsafe_allow_html=True)

    # 1. OBTENER TASA (Respetando tu ID:1)
    res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0

    # Inicializar estado si no existe
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

    # --- 2. ESCÁNER ACTIVO ---
    foto = st.camera_input("📷 ESCANEAR CÓDIGO")
    
    if foto and pyzbar:
        # Procesar la imagen
        img = Image.open(foto)
        img_np = np.array(img)
        decoded_objects = pyzbar.decode(img_np)
        
        if decoded_objects:
            # Extraer el código y limpiar (quitando el 0 inicial si es UPC-A)
            codigo_detectado = str(decoded_objects[0].data.decode('utf-8')).strip()
            if codigo_detectado.startswith('0') and len(codigo_detectado) > 10:
                codigo_detectado = codigo_detectado[1:]
            
            # GUARDAR EN EL CAMPO Y RECARGAR
            st.session_state.f["cod"] = codigo_detectado
            
            # BUSQUEDA AUTOMÁTICA: Si el producto ya existe en Supabase, traer los datos
            res_b = supabase.table("productos").select("*").eq("codigo", codigo_detectado).execute()
            if res_b.data:
                p = res_b.data[0]
                st.session_state.f.update({
                    "nom": p.get('nombre', ''),
                    "cbs": float(p.get('costo_bs', 0)),
                    "cusd": float(p.get('costo_usd', 0)),
                    "mar": float(p.get('margen', 25)),
                    "vbs": float(p.get('venta_bs', 0)),
                    "vusd": float(p.get('venta_usd', 0))
                })
                st.success(f"✅ Producto encontrado: {p.get('nombre')}")
            else:
                st.warning(f"🆕 Código nuevo: {codigo_detectado}. Completa los datos.")
            
            st.rerun() # Para que el código aparezca en el campo de texto abajo
        else:
            st.error("❌ No se pudo leer el código. Intenta con más luz o alejando un poco la cámara.")

    # --- 3. FORMULARIO (Se llena con st.session_state.f['cod']) ---
    with st.container():
        c1, c2 = st.columns([1, 2])
        # Aquí el valor viene de lo que detectó la cámara
        cod_in = c1.text_input("Código:", value=st.session_state.f["cod"])
        nom_in = c2.text_input("Producto:", value=st.session_state.f["nom"])
        
        # ... (Resto de los campos de costos y ventas con tu lógica 360)
