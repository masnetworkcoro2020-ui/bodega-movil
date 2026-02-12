import streamlit as st
from supabase import create_client
import inventario

# Configuración inicial
st.set_page_config(page_title="Bodega 360", layout="centered")

# Conexión espejo con Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.image("logo.png", width=250)
    st.title("BODEGA 360")
    st.subheader("Acceso exclusivo para Administradores")
    
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    
    if st.button("ACCEDER AL SISTEMA"):
        # Lógica de login espejo de main.py
        if u == "jmaar" and p == "15311751":
            st.session_state.autenticado = True
            st.rerun()
        else:
            try:
                res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            except:
                st.error("Error al conectar con Supabase")

if not st.session_state.autenticado:
    login()
else:
    # Menú lateral espejo
    st.sidebar.write(f"👤 Usuario: **{st.session_state.get('usuario', 'Admin')}**")
    if st.sidebar.button("SALIR"):
        st.session_state.autenticado = False
        st.rerun()
    
    inventario.mostrar(supabase)
