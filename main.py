import streamlit as st
from supabase import create_client

# --- CREDENCIALES RECUPERADAS ---
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Bodega Móvil", layout="centered")

# --- LOGIN (DATOS DE TU DASHBOARD) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Bodega Pro")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR"):
        # Usando tus credenciales maestras: jmaar / 15311751
        if usuario == "jmaar" and clave == "15311751":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
    st.stop()

# --- INTERFAZ DE INVENTARIO ---
st.header("📦 Control de Inventario")

# Obtener Tasa Actual (ID: 1)
try:
    res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa = float(res.data[0]['valor']) if res.data else 40.0
except:
    tasa = 40.0

st.info(f"Tasa de Cambio: {tasa} Bs/$")

# Campos para el producto
cod = st.text_input("Código")
nom = st.text_input("Nombre del Producto")
cbs = st.number_input("Costo en Bs", min_value=0.0, format="%.2f")

# Cálculo de Protección de Reposición (Margen 25%)
if cbs > 0:
    cusd = cbs / tasa
    vusd = cusd * 1.25
    vbs = vusd * tasa
    
    st.success(f"Venta Sugerida: {vbs:.2f} Bs ({vusd:.2f} $)")

if st.button("💾 GUARDAR PRODUCTO", use_container_width=True):
    if cod and nom:
        datos = {
            "codigo": cod.upper(),
            "nombre": nom.upper(),
            "costo_bs": cbs,
            "venta_bs": (cbs / tasa * 1.25 * tasa) if cbs > 0 else 0
        }
        try:
            supabase.table("productos").upsert(datos).execute()
            st.toast("¡Producto guardado con éxito!")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.warning("Por favor rellena Código y Nombre")
