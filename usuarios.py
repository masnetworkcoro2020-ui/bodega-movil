
import streamlit as st
import time

def login_screen(supabase):
    # Centrar el formulario de login
    st.markdown("<h1 style='text-align: center;'>🔐 ACCESO BODEGA 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Solo personal autorizado (Administradores)</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        u = st.text_input("Usuario", placeholder="Escribe tu usuario...")
        p = st.text_input("Clave", type="password", placeholder="Escribe tu clave...")
        submit = st.form_submit_button("ENTRAR AL SISTEMA", use_container_width=True)

        if submit:
            if u and p:
                try:
                    # Buscamos al usuario en la tabla original
                    # Filtramos por usuario, clave y que el rol sea administrador
                    res = supabase.table("usuarios")\
                        .select("*")\
                        .eq("usuario", u)\
                        .eq("clave", p)\
                        .execute()

                    if res.data:
                        # Verificamos si es administrador (ajusta el nombre de la columna si es diferente)
                        # Asumiendo que existe una columna 'rol' o 'nivel'
                        # Si no estás seguro del nombre de la columna del rol, me avisas
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = res.data[0]['usuario']
                        st.success(f"✅ ¡Bienvenido {u.upper()}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Usuario, clave incorrecta o no tienes permisos de administrador.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
            else:
                st.warning("Por favor, completa ambos campos.")

def mostrar(supabase):
    # Este es el módulo para gestionar usuarios una vez dentro
    st.title("👥 Gestión de Usuarios")
    st.info("Aquí podrás ver los usuarios registrados en el sistema original.")
    
    res = supabase.table("usuarios").select("usuario, clave").execute()
    if res.data:
        import pandas as pd
        df = pd.DataFrame(res.data)
        st.table(df)
