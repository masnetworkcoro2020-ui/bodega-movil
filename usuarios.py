import streamlit as st
import time

def login_screen(supabase):
    st.markdown("<h1 style='text-align: center;'>🔐 ACCESO BODEGA 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Panel de Control Móvil</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        submit = st.form_submit_button("ENTRAR", use_container_width=True)

        if submit:
            try:
                # Buscamos al usuario y su clave
                res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
                
                if res.data:
                    user_data = res.data[0]
                    # Filtro de seguridad: Solo Administrador o maestro
                    # Usamos .lower() para evitar problemas con mayúsculas
                    rol_usuario = str(user_data.get('rol', '')).lower()
                    
                    if rol_usuario in ['administrador', 'maestro']:
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = u
                        st.session_state.rol_actual = user_data.get('rol')
                        st.success(f"✅ Acceso concedido: {u}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("🚫 Error: Tu rol de '" + user_data.get('rol') + "' no tiene permiso para acceder al móvil.")
                else:
                    st.error("❌ Usuario o clave incorrectos.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

def mostrar(supabase):
    st.markdown(f"### 👤 Perfil: {st.session_state.usuario_actual}")
    st.write(f"**Nivel de acceso:** {st.session_state.rol_actual}")
    st.divider()
    st.info("Desde este módulo podrás gestionar accesos en el futuro.")
