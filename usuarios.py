import streamlit as st
import time

def login_screen(supabase):
    st.markdown("""
        <style>
        .login-box {
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #333;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🔐 BODEGA 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Acceso exclusivo para Administradores</p>", unsafe_allow_html=True)
    
    with st.container():
        u = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        p = st.text_input("🔑 Clave", type="password", placeholder="Ingresa tu clave")
        
        if st.button("ACCEDER AL SISTEMA", use_container_width=True):
            if u and p:
                try:
                    # Buscamos al usuario en la tabla exacta de tu Supabase
                    res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
                    
                    if res.data:
                        user_data = res.data[0]
                        # REGLA DE ORO: Solo entra el maestro (jmaar) o el rol Administrador
                        rol = str(user_data.get('rol', '')).lower()
                        usuario_nombre = user_data.get('usuario')

                        if rol in ['administrador', 'maestro'] or usuario_nombre == 'jmaar':
                            st.session_state.autenticado = True
                            st.session_state.usuario_actual = usuario_nombre
                            st.session_state.rol_actual = rol
                            st.success(f"✅ ¡Bienvenido, {usuario_nombre}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"🚫 Acceso Denegado: Tu rol de '{rol}' no tiene permisos para usar la App móvil.")
                    else:
                        st.error("❌ Usuario o clave incorrectos.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
            else:
                st.warning("⚠️ Por favor completa ambos campos.")

def mostrar_perfil():
    st.markdown(f"## 👤 Usuario: {st.session_state.get('usuario_actual', 'Desconocido')}")
    st.markdown(f"**Nivel de Acceso:** {st.session_state.get('rol_actual', 'Sin Rol').upper()}")
    st.divider()
    if st.button("🚪 CERRAR SESIÓN SEGURA", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
