import streamlit as st
import time
import os

def login_screen(supabase):
    # Centrar todo el contenido
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 1. MOSTRAR EL LOGO
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            # Si por algo no carga el logo, ponemos un icono por defecto
            st.markdown("<h1 style='text-align: center;'>🏪</h1>", unsafe_allow_html=True)

        st.markdown("<h1 style='text-align: center; color: #f1c40f; margin-top: -20px;'>BODEGA 360</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Panel de Control Administrativo</p>", unsafe_allow_html=True)
        
        # Formulario de login
        with st.form("login_form"):
            u = st.text_input("👤 Usuario")
            p = st.text_input("🔑 Clave", type="password")
            submit = st.form_submit_button("ENTRAR AL SISTEMA", use_container_width=True)

            if submit:
                try:
                    res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
                    
                    if res.data:
                        user_data = res.data[0]
                        rol = str(user_data.get('rol', '')).lower()
                        
                        # Filtro de seguridad
                        if rol in ['administrador', 'maestro'] or u == 'jmaar':
                            st.session_state.autenticado = True
                            st.session_state.usuario_actual = u
                            st.session_state.rol_actual = rol
                            st.success(f"✅ Bienvenido, {u}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("🚫 Acceso denegado: Solo administradores.")
                    else:
                        st.error("❌ Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

def mostrar_perfil():
    st.markdown(f"## 👤 Perfil: {st.session_state.usuario_actual}")
    st.write(f"**Nivel de acceso:** {st.session_state.rol_actual.upper()}")
    st.divider()
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
