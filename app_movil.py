import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image

# 1. CONEXIÓN (Tus credenciales blindadas)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. CONFIGURACIÓN Y ESTILOS (Formato teléfono robusto)
st.set_page_config(page_title="BODEGA MOVIL 360", layout="centered")
st.markdown("""
    <style>
    .stNumberInput input, .stTextInput input { height: 50px !important; font-size: 18px !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black; font-weight: bold; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta $")) input { background-color: #d6eaf8 !important; color: black; }
    .stButton>button { width: 100%; height: 60px !important; border-radius: 12px; font-weight: bold; font-size: 20px !important; }
    .user-card { background-color: #f8f9fa; padding: 12px; border-radius: 10px; border-left: 5px solid #1f538d; margin-bottom: 8px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEMA DE LOGIN (CANDADO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>🔐 ACCESO BODEGA 360</h2>", unsafe_allow_html=True)
    u_acc = st.text_input("Usuario:")
    p_acc = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR AL SISTEMA"):
        # Verificación directa en Supabase
        res_auth = supabase.table("usuarios").select("*").eq("usuario", u_acc).eq("clave", p_acc).execute()
        if res_auth.data:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Usuario o Clave incorrectos, mano.")
    st.stop() # No deja pasar nada de lo que sigue si no hay login

# --- 4. SI PASA EL LOGIN, CARGA TODO EL SISTEMA ---

# OBTENCIÓN DE TASA (ID:1)
try:
    res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0
except Exception as e:
    st.error(f"Error de conexión con la tasa: {e}")
    tasa_v = 40.0

# Botón para cerrar sesión en el menú lateral
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# PESTAÑAS PRINCIPALES
tab1, tab2, tab3 = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

# --- PESTAÑA 1: TASA ---
with tab1:
    st.subheader("Ajuste de Tasa Diaria")
    st.info(f"Tasa actual en sistema: {tasa_v} Bs/$")
    nt = st.number_input("Nueva Tasa:", value=tasa_v, format="%.2f")
    if st.button("💾 ACTUALIZAR TASA GLOBAL"):
        supabase.table("ajustes").update({"valor": nt}).eq("id", 1).execute()
        st.success("Tasa actualizada correctamente en la nube.")
        st.rerun()

# --- PESTAÑA 2: INVENTARIO (MOTOR 360 COMPLETO) ---
with tab2:
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
    
    st.camera_input("📷 REGISTRO FOTOGRÁFICO")

    # BUSCADOR DINÁMICO
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    opciones = ["-- NUEVO PRODUCTO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    seleccion = st.selectbox("🔍 Buscar producto para editar:", opciones)

    # Carga de datos al seleccionar
    if seleccion != "-- NUEVO PRODUCTO --" and seleccion != st.session_state.get("last_sel"):
        p = df_lista[df_lista['nombre'] == seleccion].iloc[0]
        st.session_state.f = {
            "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
            "mar": float(p['margen']), "vbs": float(p['venta_bs']),
            "vusd": float(p['venta_usd']), "cod": str(p['codigo']), "nom": str(p['nombre'])
        }
        st.session_state.last_sel = seleccion
    elif seleccion == "-- NUEVO PRODUCTO --" and st.session_state.get("last_sel") != "-- NUEVO PRODUCTO --":
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
        st.session_state.last_sel = "-- NUEVO PRODUCTO --"

    # CAMPOS DE DATOS
    cod_in = st.text_input("Código de Barras:", value=st.session_state.f["cod"])
    nom_in = st.text_input("Nombre del Producto:", value=st.session_state.f["nom"])
    
    col_c1, col_c2 = st.columns(2)
    in_cbs = col_c1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = col_c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    
    in_mar = st.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    
    col_v1, col_v2 = st.columns(2)
    in_vusd = col_v1.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = col_v2.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # --- MOTOR 360° TOTAL (SIN RECORTES) ---
    factor = (1 + (in_mar / 100))

    # A. Costo Bs -> Adelante
    if in_cbs != st.session_state.f["cbs"]:
        st.session_state.f["cbs"] = in_cbs
        st.session_state.f["cusd"] = in_cbs / tasa_v
        st.session_state.f["vusd"] = st.session_state.f["cusd"] * factor
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # B. Costo $ -> Adelante
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f["cusd"] = in_cusd
        st.session_state.f["cbs"] = in_cusd * tasa_v
        st.session_state.f["vusd"] = in_cusd * factor
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # C. Margen -> Adelante
    elif in_mar != st.session_state.f["mar"]:
        st.session_state.f["mar"] = in_mar
        st.session_state.f["vusd"] = st.session_state.f["cusd"] * factor
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # D. Venta Bs -> Atrás
    elif in_vbs != st.session_state.f["vbs"]:
        st.session_state.f["vbs"] = in_vbs
        st.session_state.f["vusd"] = in_vbs / tasa_v
        st.session_state.f["cusd"] = (in_vbs / tasa_v) / factor
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()

    # E. Venta $ -> Atrás
    elif in_vusd != st.session_state.f["vusd"]:
        st.session_state.f["vusd"] = in_vusd
        st.session_state.f["vbs"] = in_vusd * tasa_v
        st.session_state.f["cusd"] = in_vusd / factor
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()

    # ACCIONES
    if st.button("💾 GUARDAR / ACTUALIZAR EN NUBE"):
        datos = {
            "codigo": cod_in.upper(), "nombre": nom_in.upper(),
            "costo_bs": st.session_state.f["cbs"], "costo_usd": st.session_state.f["cusd"],
            "margen": st.session_state.f["mar"], "venta_usd": st.session_state.f["vusd"], "venta_bs": st.session_state.f["vbs"]
        }
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Producto guardado exitosamente!")
        st.rerun()

    if st.button("🗑️ ELIMINAR PRODUCTO", type="secondary"):
        if nom_in:
            supabase.table("productos").delete().eq("nombre", nom_in).execute()
            st.warning("Producto eliminado de la base de datos.")
            st.rerun()

    # TABLA DE CONSULTA
    st.divider()
    st.subheader("📋 Inventario Registrado")
    if not df_lista.empty:
        st.dataframe(df_lista[["nombre", "venta_bs", "costo_usd", "margen"]], use_container_width=True, hide_index=True)

# --- PESTAÑA 3: USUARIOS ---
with tab3:
    st.subheader("👥 Gestión de Accesos")
    with st.expander("➕ Crear Nuevo Usuario"):
        u_nom = st.text_input("Nombre de Usuario:")
        u_cla = st.text_input("Clave de Acceso:", type="password")
        if st.button("REGISTRAR USUARIO"):
            if u_nom and u_cla:
                supabase.table("usuarios").insert({"usuario": u_nom, "clave": u_cla, "rol": "Vendedor"}).execute()
                st.success(f"Usuario {u_nom} creado.")
                st.rerun()

    st.divider()
    res_u = supabase.table("usuarios").select("*").execute()
    if res_u.data:
        for usr in res_u.data:
            st.markdown(f'<div class="user-card"><b>👤 {usr["usuario"]}</b></div>', unsafe_allow_html=True)
            if st.button(f"Borrar {usr['usuario']}", key=f"del_{usr['usuario']}"):
                supabase.table("usuarios").delete().eq("usuario", usr['usuario']).execute()
                st.rerun()
