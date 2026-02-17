# config.py
from supabase import create_client, Client
import streamlit as st
import os

# --- CREDENCIALES DE TU BODEGA (SUPABASE) ---
# He mantenido tus credenciales actuales del proyecto 'aznkqqrakzhvbtlnjaxz'
SUPABASE_URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

def conectar():
    """
    Establece la conexión con Supabase.
    Detecta automáticamente si estás en la Web (Streamlit) o en Local (PC).
    """
    try:
        # 1. Intenta leer desde Secrets (Streamlit Cloud - Para el celular)
        if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            return create_client(url, key)
        
        # 2. Si no hay secrets (o estás en PC), usa las variables de arriba
        return create_client(SUPABASE_URL, SUPABASE_KEY)
        
    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")
        return None

# --- CONFIGURACIÓN VISUAL (Mantenemos los colores de Royal Essence) ---
COLOR_FONDO = "#0D1B2A"
COLOR_SIDEBAR = "#1B263B"
COLOR_DORADO = "#C5A059"
COLOR_TEXTO = "#E0E1DD"
COLOR_INPUT = "#34495E"

# Nota: Este archivo ya no necesita sqlite3 porque todo va a la nube.
