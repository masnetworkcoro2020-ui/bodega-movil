import streamlit as st
from supabase import create_client

# Sacamos las llaves de los Secrets de Streamlit por seguridad
SUPABASE_URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

def conectar():
    """Establece la conexión con Supabase para la versión Web"""
    try:
        return create_client(URL, KEY)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None
