import streamlit as st
from supabase import create_client
import sys

# --- CONFIGURACIÓN ESPEJO BODEGA 2.0 ---

# 1. Intentamos sacar las llaves de los Secrets (Configuración de Streamlit Cloud)
# 2. Si no existen, usamos las llaves directas (Hardcoded) para asegurar que abra
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
except:
    # Llaves extraídas directamente de tu archivo config.py original
    URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
    KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

def conectar():
    """Establece la conexión con Supabase verificando la validez de la URL"""
    if not URL or "https" not in URL:
        st.error("❌ Error: La URL de Supabase no es válida o está vacía.")
        return None
        
    try:
        # Creamos el cliente exactamente como en tu versión de escritorio
        client = create_client(URL, KEY)
        return client
    except Exception as e:
        st.error(f"❌ Error crítico de conexión: {e}")
        return None
