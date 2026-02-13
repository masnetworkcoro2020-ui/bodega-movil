import streamlit as st
from supabase import create_client

# 1. Configuración de conexión (Tus llaves de Supabase)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Bodega Movil", layout="centered")

if 'login' not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Acceso via Supabase")
    usuario_input = st.text_input("Usuario")
    clave_input = st.text_input("Clave", type="password")
    
    if st.button("Entrar"):
        # --- AQUÍ ES DONDE BUSCA EN SUPABASE ---
        # Busca en la tabla 'usuarios' donde el nombre coincida
        query = supabase.table("usuarios").select("*").eq("usuario", usuario_input).execute()
        
        if query.data:
            # Si el usuario existe, revisa si la clave coincide
            user_db = query.data[0]
            if user_db["clave"] == clave_input:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        else:
            st.error("El usuario no existe en la base de datos")
    st.stop()
