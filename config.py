import streamlit as st
from supabase import create_client

# Estas son tus llaves originales, limpias de espacios
URL_MAESTRA = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY_MAESTRA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

def conectar():
    try:
        # Forzamos la conexión con las llaves directas para que no dependa de nada externo
        client = create_client(URL_MAESTRA, KEY_MAESTRA)
        return client
    except Exception as e:
        st.error(f"Error en config.py: {e}")
        return None
