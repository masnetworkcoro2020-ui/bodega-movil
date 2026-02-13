import streamlit as st
from supabase import create_client

# 1. LAS LLAVES DE LA CORONA (El mensajero que va a Supabase)
URL_SUPA = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY_SUPA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

# Conectamos
supabase = create_client(URL_SUPA, KEY_SUPA)

# 2. SEGURIDAD (Si no pasó por el login, lo mandamos de vuelta)
if 'auth' not in st.session_state or not st.session_state.auth:
    st.switch_page("main.py")

st.title("📦 Buscador de Inventario")

# Botón para regresar al panel
if st.button("⬅️ Volver al Panel"):
    st.switch_page("main.py")

# 3. EL BUSCADOR (La orden de buscar en las tablas)
codigo = st.text_input("Escribe o escanea el código:")

if codigo:
    # Aquí le decimos: "Ve a Supabase, busca en la tabla 'productos' donde el 'codigo' sea igual a este"
    res = supabase.table("productos").select("*").eq("codigo", codigo).execute()
    
    if res.data:
        p = res.data[0]
        st.success(f"✅ PRODUCTO: {p['nombre']}")
        st.metric("PRECIO $", f"{p['precio_dol']}")
    else:
        st.error("❌ Ese código no existe en la base de datos.")
