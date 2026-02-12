import streamlit as st
from supabase import create_client

# --- LLAVES MAESTRAS EXTRAÍDAS DE TU ARCHIVO ORIGINAL ---
# Las ponemos directas aquí para que no dependan de los Secrets si están fallando
URL_FIJA = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY_FIJA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

def conectar():
    """Conexión espejo definitiva"""
    try:
        # Primero intentamos usar los Secrets de Streamlit si existen
        if "SUPABASE_URL" in st.secrets:
            u = st.secrets["SUPABASE_URL"].strip()
            k = st.secrets["SUPABASE_KEY"].strip()
            return create_client(u, k)
        else:
            # Si no hay secretos, usamos las llaves fijas
            return create_client(URL_FIJA, KEY_FIJA)
    except Exception as e:
        st.error(f"Error al conectar: {e}")
        return None
