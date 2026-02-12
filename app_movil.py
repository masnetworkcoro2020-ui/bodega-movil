import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Tus credenciales blindadas)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS MÓVIL (Respetando los colores de tu inventario.py)
st.set_page_config(page_title="BODEGA MOVIL 360", layout="centered")
st.markdown("""
    <style>
    .stNumberInput input, .stTextInput input { height: 50px !important; font-size: 18px !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black; font-weight: bold; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta $")) input { background-color: #d6eaf8 !important; color: black; }
    .stButton>button { width: 100%; height: 55px !important; border-radius: 12px; font-weight: bold; }
    .user-card { background-color: #f8f9fa; padding: 12px; border-radius: 10px; border-left: 5px solid #1f538d; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. OBTENER TASA (ID:1)
try:
    res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0
except:
    tasa_v = 40.0

# --- ESTRUCTURA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with tab1:
    st.subheader("Control de Cambio")
    nt = st.number_input("Tasa Actual:", value=tasa_v, format="%.2f")
    if st.button("💾 GUARDAR NUEVA TASA"):
        supabase.table("ajustes").update({"valor": nt}).eq("id", 1).execute()
        st.success("Tasa actualizada")
        st.rerun()

with tab2:
    # Session State para no perder el rastro de los cambios
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
    
    # Cámara
    st.camera_input("📷 ESCANEAR CÓDIGO")

    # Buscador Inteligente
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    opciones = ["-- NUEVO PRODUCTO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    seleccion = st.selectbox("🔍 Buscar producto registrado:", opciones)

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
    cod_in = st.text_input("Código:", value=st.session_state.f["cod"])
    nom_in = st.text_input("Nombre del Producto:", value=st.session_state.f["nom"])
    
    col_c1, col_c2 = st.columns(2)
    in_cbs = col_c1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = col_c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    
    in_mar = st.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    
    col_v1, col_v2 = st.columns(2)
    in_vusd = col_v1.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = col_v2.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # --- MOTOR 360° TOTAL (Lógica de inventario.py) ---
    
    # A. Cambio en Costo Bs -> Empuja todo
    if in_cbs != st.session_state.f["cbs"]:
        st.session_state.f["cbs"] = in_cbs
        st.session_state.f["cusd"] = in_cbs / tasa_v
        st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # B. Cambio en Costo $ -> Empuja todo
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f["cusd"] = in_cusd
        st.session_state.f["cbs"] = in_cusd * tasa_v
        st.session_state.f["vusd"] = in_cusd * (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # C. Cambio en Margen -> Recalcula ventas
    elif in_mar != st.session_state.f["mar"]:
        st.session_state.f["mar"] = in_mar
        st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (in_mar/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # D. Cambio en Venta Bs -> Recalcula hacia atrás
    elif in_vbs != st.session_state.f["vbs"]:
        st.session_state.f["vbs"] = in_vbs
        st.session_state.f["vusd"] = in_vbs / tasa_v
        if st.session_state.f["cusd"] > 0:
            st.session_state.f["mar"] = ((st.session_state.f["vusd"] / st.session_state.f["cusd"]) - 1) * 100
        st.rerun()

    # E. Cambio en Venta $ -> Recalcula hacia atrás
    elif in_vusd != st.session_state.f["vusd"]:
        st.session_state.f["vusd"] = in_vusd
        st.session_state.f["vbs"] = in_vusd * tasa_v
        if st.session_state.f["cusd"] > 0:
            st.session_state.f["mar"] = ((in_vusd / st.session_state.f["cusd"]) - 1) * 100
        st.rerun()

    # BOTONES DE ACCIÓN
    if st.button("💾 GUARDAR / ACTUALIZAR PRODUCTO"):
        datos = {
            "codigo": cod_in.upper(), "nombre": nom_in.upper(),
            "costo_bs": st.session_state.f["cbs"], "costo_usd": st.session_state.f["cusd"],
            "margen": st.session_state.f["mar"], "venta_usd": st.session_state.f["vusd"], "venta_bs": st.session_state.f["vbs"]
        }
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Datos guardados en la nube!")
        st.rerun()

    if st.button("🗑️ ELIMINAR PRODUCTO", type="secondary"):
        supabase.table("productos").delete().eq("nombre", nom_in).execute()
        st.rerun()

    # TABLA DE CONSULTA
    st.divider()
    st.subheader("📋 Inventario Actual")
    if not df_lista.empty:
        st.dataframe(df_lista[["nombre", "venta_bs", "costo_usd", "margen"]], use_container_width=True, hide_index=True)

with tab3:
    st.subheader("👥 Usuarios")
    # Lógica completa de usuarios
    with st.expander("➕ Nuevo Usuario"):
        u_n = st.text_input("Usuario")
        u_p = st.text_input("Clave", type="password")
        if st.button("CREAR"):
            supabase.table("usuarios").insert({"usuario": u_n, "clave": u_p, "rol": "Vendedor"}).execute()
            st.rerun()
    
    u_list = supabase.table("usuarios").select("*").execute()
    for usr in u_list.data:
        st.markdown(f'<div class="user-card"><b>{usr["usuario"]}</b></div>', unsafe_allow_html=True)
