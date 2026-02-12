import streamlit as st
from supabase import create_client

# Credenciales centralizadas
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Tu clave completa

def get_supabase():
    return create_client(URL, KEY)
