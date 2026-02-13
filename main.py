import streamlit as st
from supabase import create_client
from streamlit_barcode_scanner import st_barcode_scanner # Necesitas agregar esto a requirements.txt

# --- CONEXIÓN (MANTENIENDO TUS CREDENCIALES) ---
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Bodega Pro - Inventario", layout="centered")

# --- LÓGICA DE ACCESO (MANTENIDA) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR"):
        if u == "jmaar" and p == "15311751":
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# --- MODULO INVENTARIO (TU LOGICA ORIGINAL) ---
st.title("📦 Inventario Pro")

# 1. Obtener Tasa ID:1
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_actual = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_actual = 40.0

st.info(f"Tasa de Cambio: {tasa_actual} Bs/$")

# --- ESCÁNER EN VIVO (CÁMARA TRASERA) ---
st.subheader("📷 Escanear Producto")
barcode = st_barcode_scanner(device_id="environment") # "environment" fuerza la cámara trasera

if barcode:
    st.write(f"Código detectado: **{barcode}**")
    # Buscar producto automáticamente
    res_prod = supabase.table("productos").select("*").eq("codigo", barcode).execute()
    if res_prod.data:
        st.session_state.datos_prod = res_prod.data[0]
        st.success("Producto encontrado")
    else:
        st.session_state.datos_prod = {"codigo": barcode, "nombre": "", "costo_bs": 0.0}
        st.warning("Producto nuevo")

# --- CAMPOS DE ENTRADA (COLORES ORIGINALES) ---
st.divider()

# Preparar variables según tu archivo
dp = st.session_state.get('datos_prod', {"codigo": "", "nombre": "", "costo_bs": 0.0})

cod = st.text_input("CÓDIGO", value=dp.get('codigo', ""))
nom = st.text_input("NOMBRE DEL PRODUCTO", value=dp.get('nombre', ""))

# Campo Amarillo: Costo Bs
st.markdown('<p style="background-color:#fcf3cf; padding:5px; border-radius:5px; font-weight:bold;">COSTO EN BS (CAMPO AMARILLO)</p>', unsafe_allow_html=True)
cbs = st.number_input("Introduzca Costo Bs", value=float(dp.get('costo_bs', 0.0)), format="%.2f", label_visibility="collapsed")

# Lógica de Protección de Reposición (360°)
margen = 25 # Tu margen estándar del 25%
cusd = cbs / tasa_actual if tasa_actual > 0 else 0
vusd = cusd * (1 + (margen/100))
vbs = vusd * tasa_actual

# Campo Verde: Venta Bs
st.markdown('<p style="background-color:#d4efdf; padding:5px; border-radius:5px; font-weight:bold;">VENTA SUGERIDA BS (CAMPO VERDE)</p>', unsafe_allow_html=True)
st.metric(label="Venta en Bolívares", value=f"{vbs:.2f} Bs")
st.write(f"Equivalente a: **{vusd:.2f} $**")

# --- BOTÓN GUARDAR (UPSERT ORIGINAL) ---
if st.button("💾 GUARDAR EN BODEGA", use_container_width=True):
    if cod and nom:
        datos_guardar = {
            "codigo": cod.upper(),
            "nombre": nom.upper(),
            "costo_bs": cbs,
            "venta_bs": vbs,
            "venta_usd": vusd,
            "margen": margen
        }
        try:
            supabase.table("productos").upsert(datos_guardar).execute()
            st.toast("✅ ¡Guardado con éxito!", icon="🎉")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.error("Faltan datos obligatorios")
