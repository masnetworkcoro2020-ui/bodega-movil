import streamlit as st
from supabase import create_client

def conectar():
    # Usa las credenciales guardadas en Secrets de Streamlit Cloud
    url = st.secrets["URL"]
    key = st.secrets["KEY"]
    return create_client(url, key)
