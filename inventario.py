import streamlit as st
from supabase import create_client
from camera_input_live import camera_input_live
from pyzbar import pyzbar
from PIL import Image

# 1. SEGURIDAD Y CONEXIÓN
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("main.py")

URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# --- FUNCIÓN: BUSCAR TASA ID:1 ---
def obtener_tasa():
    res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    return float(res.data[0]['valor']) if res.data else 40.0

tasa = obtener_tasa()

st.title("📦 Inventario Bodega")
if st.button("⬅️ Volver al Panel"):
    st.switch_page("main.py")

# 2. MÓDULO DE ESCANEO EN VIVO
st.subheader("📷 Escáner de Cámara")
imagen_camara = camera_input_live()

codigo_detectado = ""
if imagen_camara:
    img = Image.open(imagen_camara)
    barcodes = pyzbar.decode(img)
    for barcode in barcodes:
        codigo_detectado = barcode.data.decode('utf-8')
        st.success(f"Código detectado: {codigo_detectado}")

# 3. BUSCADOR (Manual o por Escáner)
codigo = st.text_input("Código de barras:", value=codigo_detectado)

if codigo:
    res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
    
    if res.data:
        p = res.data[0]
        # TU LÓGICA ORIGINAL DE PROTECCIÓN
        c_usd = float(p.get('costo_usd', 0))
        margen = float(p.get('margen', 25))
        v_usd = c_usd * (1 + (margen / 100))
        v_bs = v_usd * tasa
        
        st.divider()
        st.success(f"✅ PRODUCTO: {p['nombre']}")
        
        c1, c2 = st.columns(2)
        c1.metric("Precio Ref ($)", f"{v_usd:.2f} $")
        c2.metric("Precio Final (Bs)", f"{v_bs:.2f} Bs")
        
        st.info(f"Cálculo basado en Tasa BCV: {tasa} Bs.")
    else:
        st.error("Producto no encontrado.")
