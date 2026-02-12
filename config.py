import streamlit as st
from supabase import create_client

# Sacamos las llaves de los Secrets de Streamlit por seguridad
UPABASE_URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
SUPABASE_KEY = "tu_llave_anon_aquí"

def conectar():
    """Establece la conexión con Supabase para la versión Web"""
    try:
        return create_client(URL, KEY)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None
