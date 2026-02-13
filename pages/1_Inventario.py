import streamlit as st
from supabase import create_client

# --- EL CANDADO DE SEGURIDAD ---
if 'auth' not in st.session_state or not st.session_state.auth:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    if st.button("Ir al Login"):
        st.switch_page("main.py")
    st.stop() # Esto detiene el código aquí si no estás logueado

# --- SI PASA EL CANDADO, CARGA EL RESTO ---
# (Aquí pones tu conexión a Supabase y el resto de tu código de inventario)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
# ... resto del código
