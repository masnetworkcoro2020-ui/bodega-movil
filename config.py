import streamlit as st
from supabase import create_client

# Sacamos las llaves de los Secrets de Streamlit por seguridad
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

def conectar():
    """Establece la conexión con Supabase para la versión Web"""
    try:
        return create_client(URL, KEY)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None
