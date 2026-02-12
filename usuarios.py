import streamlit as st
import time
import os

def login_screen(supabase):
    # Usamos columnas para centrar el contenido en el móvil
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. CARGAR EL LOGO DESDE GITHUB
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>🏪</h1>", unsafe_allow_html=True)

        # 2. TÍTULO Y SUBTÍTULO
        st.markdown("""
            <h2 style='text-align: center; color: #f1c40f; margin-bottom: 0px;'>BODEGA 360</h2>
            <p style='text-align: center; color: #888; font-size: 0.9em;'>Acceso exclusivo para Administradores</p>
            <hr style='border: 0.5px solid #333;'>
        """, unsafe_allow_html=True)
        
        # 3. FORMULARIO DE ACCESO
        with st.form("login_form"):
            u = st.text_input("👤 Usuario", placeholder="Ej: jmaar")
            p = st.text_input("🔑 Clave", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("ACCEDER AL SISTEMA", use_container_width=True)

            if submit:
                if u and p:
                    try:
                        # Buscamos en tu tabla de usuarios
                        res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
                        
                        if res.data:
                            user_data = res.data[0]
                            rol = str(user_data.get('rol', '')).lower()
                            
                            # Filtro: Solo 'maestro' (jmaar) o 'Administrador' (Esmeralda)
                            if rol in ['administrador', 'maestro'] or u == 'jmaar':
                                st.session_state.autenticado = True
                                st.session_state.usuario_actual = u
                                st.session_state.rol_actual = rol
                                st.success(f"✅ ¡Bienvenido, {u}!")
                                time.sleep(1.2)
                                st.rerun()
                            else:
                                st.error("🚫 Tu rol no tiene permiso para entrar aquí.")
                        else:
                            st.error("❌ Usuario o clave incorrectos.")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
                else:
                    st.warning("⚠️ Completa los datos para continuar.")

def mostrar_perfil():
    st.markdown(f"### 👤 Sesión de: {st.session_state.get('usuario_actual', 'Admin')}")
    st.info(f"Nivel de acceso detectado: **{st.session_state.get('rol_actual', 'ADMIN').upper()}**")
    st.divider()
    if st.button("🚪 CERRAR SESIÓN SEGURA", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
