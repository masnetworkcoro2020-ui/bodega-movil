import streamlit as st
from config import conectar  # Usa tu lógica de conexión original
import inventario

# 1. Configuración de la Ventana (Espejo de tu Dashboard zoomed)
st.set_page_config(
    page_title="SISTEMA BODEGA PRO 2.0", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# 2. Establecer conexión inicial
if 'supabase' not in st.session_state:
    st.session_state.supabase = conectar()

# 3. Estado de autenticación
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.rol = "Operador"

def login():
    """Replica exacta de tu login.py y main.py"""
    # Intentamos cargar el logo si existe, si no, solo el título
    try:
        st.image("logo.png", width=250)
    except:
        st.title("BODEGA 360")

    st.subheader("Acceso exclusivo para Administradores")
    
    # Campos de entrada (Espejo de main.py)
    u = st.text_input("Usuario", key="user_input").lower().strip()
    p = st.text_input("Clave", type="password", key="pass_input").strip()
    
    if st.button("ACCEDER AL SISTEMA", use_container_width=True):
        # --- LÓGICA MAESTRA (Copiada de tu main.py) ---
        # Definimos las credenciales maestras que tienes en el código
        USER_MASTER = "jmaar"
        PASS_MASTER = "15311751"

        if u == USER_MASTER and p == PASS_MASTER:
            st.session_state.autenticado = True
            st.session_state.usuario = u
            st.session_state.rol = "Administrador"
            st.rerun()
        
        # --- BÚSQUEDA EN BASE DE DATOS ---
        elif st.session_state.supabase:
            try:
                res = st.session_state.supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
                if res.data:
                    datos = res.data[0]
                    # Buscamos el rol dinámicamente como en tu código
                    rol_final = "Operador"
                    for llave in datos.keys():
                        if "rol" in llave.lower():
                            rol_final = datos[llave]
                            break
                    
                    st.session_state.autenticado = True
                    st.session_state.usuario = u
                    st.session_state.rol = rol_final
                    st.rerun()
                else:
                    st.error("❌ Usuario o clave incorrectos")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
        else:
            st.error("Error: No hay conexión con la base de datos")

# --- FLUJO PRINCIPAL ---
if not st.session_state.autenticado:
    login()
else:
    # Sidebar espejo del Dashboard lateral
    st.sidebar.markdown(f"### 👤 {st.session_state.usuario.upper()}")
    st.sidebar.write(f"Rol: **{st.session_state.rol}**")
    st.sidebar.divider()
    
    # Menú de navegación
    opcion = st.sidebar.radio("MENÚ PRINCIPAL", ["📦 Inventario", "📊 Dashboard", "⚙️ Configuración"])
    
    if st.sidebar.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

    # Carga de módulos
    if opcion == "📦 Inventario":
        inventario.mostrar(st.session_state.supabase)
    elif opcion == "📊 Dashboard":
        st.info("Módulo de estadísticas en desarrollo para versión móvil")
    elif opcion == "⚙️ Configuración":
        st.write("Configuración del sistema")
