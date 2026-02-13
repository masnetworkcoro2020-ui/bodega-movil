import streamlit as st
from supabase import create_client
from streamlit_barcode_scanner import st_barcode_scanner

# Conexión independiente (para que no dependa de otros archivos)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# Verificar si está logueado antes de mostrar nada
if not st.session_state.get('autenticado', False):
    st.warning("⚠️ Por favor, inicia sesión en la página principal.")
    st.stop()

st.title("📦 Módulo de Inventario")

# LOGICA DE TASA ID:1
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_actual = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_actual = 40.0

st.info(f"Tasa del día: {tasa_actual} Bs/$")

# ESCÁNER (Cámara trasera)
barcode = st_barcode_scanner(device_id="environment")

# Lógica de búsqueda y autocompletado
if barcode:
    res_prod = supabase.table("productos").select("*").eq("codigo", barcode).execute()
    st.session_state.datos_prod = res_prod.data[0] if res_prod.data else {"codigo": barcode, "nombre": "", "costo_bs": 0.0}

dp = st.session_state.get('datos_prod', {"codigo": "", "nombre": "", "costo_bs": 0.0})

# INTERFAZ (Respetando colores de tu inventario.py)
cod = st.text_input("CÓDIGO", value=dp.get('codigo', ""))
nom = st.text_input("NOMBRE DEL PRODUCTO", value=dp.get('nombre', ""))

# Campo Amarillo
st.markdown('<div style="background-color:#fcf3cf; padding:10px; border-radius:5px;"><b>COSTO BS</b></div>', unsafe_allow_html=True)
cbs = st.number_input("Costo", value=float(dp.get('costo_bs', 0.0)), format="%.2f", label_visibility="collapsed")

# LÓGICA 360°
margen = 25
cusd = cbs / tasa_actual if tasa_actual > 0 else 0
vusd = cusd * 1.25
vbs = vusd * tasa_actual

# Campo Verde
st.markdown('<div style="background-color:#d4efdf; padding:10px; border-radius:5px;"><b>VENTA SUGERIDA BS</b></div>', unsafe_allow_html=True)
st.subheader(f"{vbs:.2f} Bolívares")
st.write(f"Ref: {vusd:.2f} $")

if st.button("💾 GUARDAR", use_container_width=True):
    # Tu Upsert original
    supabase.table("productos").upsert({
        "codigo": cod.upper(),
        "nombre": nom.upper(),
        "costo_bs": cbs,
        "venta_bs": vbs,
        "venta_usd": vusd
    }).execute()
    st.toast("Guardado!")
