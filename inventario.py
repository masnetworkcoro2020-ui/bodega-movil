import streamlit as st
from supabase import create_client

# 1. SEGURIDAD Y CONEXIÓN
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("main.py")

URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

@st.cache_resource
def conectar():
    return create_client(URL, KEY)

supabase = conectar()

# 2. OBTENER TASA ACTUAL
def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa = obtener_tasa()

# --- INTERFAZ ---
st.title("📦 Inventario (Protección de Reposición)")

if st.button("⬅️ Volver al Panel"):
    st.switch_page("main.py")

st.divider()

# 3. BUSCADOR Y LÓGICA DE CÁLCULO
col_busq, col_vacia = st.columns([2, 1])
with col_busq:
    codigo_buscado = st.text_input("🔍 Escanea o escribe el código:")

if codigo_buscado:
    res = supabase.table("productos").select("*").eq("codigo", codigo_buscado).execute()
    
    if res.data:
        p = res.data[0]
        st.success(f"Producto: {p['nombre']}")
        
        # Valores para recalcular (Tu lógica 360°)
        c_usd = float(p.get('costo_usd', 0))
        margen = float(p.get('margen', 25))
        v_usd = c_usd * (1 + (margen / 100))
        v_bs = v_usd * tasa
        
        # Muestra de resultados idéntica a tu diseño original
        c1, c2, c3 = st.columns(3)
        c1.metric("Costo USD", f"{c_usd:.2f} $")
        c2.metric("Margen", f"{margen}%")
        c3.metric("Venta USD", f"{v_usd:.2f} $")
        
        st.subheader(f"💰 Precio en Bolívares: {v_bs:.2f} Bs.")
        st.caption(f"Calculado a tasa: {tasa} Bs. (Protección de Reposición activa)")
    else:
        st.error("Producto no encontrado en la base de datos.")

# 4. TABLA GENERAL (Muestra tus datos guardados)
st.divider()
st.subheader("📋 Lista de Productos")
if st.button("Actualizar Lista"):
    res_todos = supabase.table("productos").select("codigo, nombre, costo_usd, margen").order("nombre").execute()
    if res_todos.data:
        st.table(res_todos.data)
