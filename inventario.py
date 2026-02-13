import streamlit as st
from supabase import create_client

# Seguridad: Si no hay auth, pa' fuera
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("main.py")

# Conexión a la Corona
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.title("📦 Inventario Bodega")
if st.button("⬅️ Volver al Panel"):
    st.switch_page("main.py")

# 1. Obtener Tasa ID:1
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# 2. Buscador
codigo = st.text_input("Escribe el código de barras:")

if codigo:
    res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
    if res.data:
        p = res.data[0]
        # Lógica Matemática Original
        costo_usd = float(p.get('costo_usd', 0))
        margen = float(p.get('margen', 25))
        venta_usd = costo_usd * (1 + (margen/100))
        venta_bs = venta_usd * tasa
        
        st.success(f"✅ PRODUCTO: {p['nombre']}")
        st.metric("VENTA BS", f"{venta_bs:.2f} Bs", help=f"Tasa: {tasa}")
    else:
        st.error("No registrado.")
