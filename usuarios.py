import streamlit as st
import time

def login_screen(supabase):
    st.markdown("<h1 style='text-align: center;'>🔐 ACCESO BODEGA 360</h1>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        submit = st.form_submit_button("ENTRAR", use_container_width=True)

        if submit:
            try:
                # Buscamos en tu tabla original de usuarios
                res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
                
                if res.data:
                    user_data = res.data[0]
                    # Validamos que sea administrador. 
                    # NOTA: Verifica si tu columna se llama 'nivel' o 'rol'. 
                    # Aquí asumo que si el usuario existe y es el que usas en PC, entra.
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = u
                    st.success(f"✅ Bienvenido, {u}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
            except Exception as e:
                st.error(f"Error de base de datos: {e}")

def mostrar(supabase):
    st.title("👥 Panel de Usuarios")
    st.write("Conectado como Administrador")
    # Aquí puedes poner una lista de usuarios luego si quieres
