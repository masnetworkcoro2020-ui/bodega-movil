import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Blindada)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. CONFIGURACIÓN Y ESTILOS (Colores de tu PC)
st.set_page_config(page_title="BODEGA PRO V2", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ACTUAL ---
def traer_tasa():
    res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    return float(res.data[0]['valor']) if res.data else 40.0

tasa_v = traer_tasa()

# --- PESTAÑAS ---
tab_tasa, tab_inv, tab_usu = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

# --- MODULO TASA ---
with tab_tasa:
    st.subheader("📊 Control de Tasa de Cambio")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("Tasa Actual", f"{tasa_v} Bs/$")
        nueva_tasa = st.number_input("Nueva Tasa (BCV/Paralelo)", value=tasa_v, format="%.2f")
        if st.button("💾 ACTUALIZAR TASA GLOBAL"):
            supabase.table("ajustes").update({"valor": nueva_tasa}).eq("id", 1).execute()
            st.success(f"¡Tasa actualizada! Todo el inventario se ajustó a {nueva_tasa}")
            st.rerun()

# --- MODULO INVENTARIO (TU LOGICA 360) ---
with tab_inv:
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

    # Buscador para editar (Lo que ya entendiste fino)
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    
    opciones = ["-- NUEVO PRODUCTO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    seleccion = st.selectbox("🔍 Buscar producto para editar/eliminar", opciones)

    if seleccion != "-- NUEVO PRODUCTO --" and seleccion != st.session_state.get("last_sel"):
        prod = df_lista[df_lista['nombre'] == seleccion].iloc[0]
        st.session_state.f = {
            "cbs": float(prod['costo_bs']), "cusd": float(prod['costo_usd']),
            "mar": float(prod['margen']), "vbs": float(prod['venta_usd'] * tasa_v),
            "vusd": float(prod['venta_usd']), "cod": str(prod['codigo']), "nom": str(prod['nombre'])
        }
        st.session_state.last_sel = seleccion
    elif seleccion == "-- NUEVO PRODUCTO --" and st.session_state.get("last_sel") != "-- NUEVO PRODUCTO --":
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
        st.session_state.last_sel = "-- NUEVO PRODUCTO --"

    # Campos de Entrada
    c_id = st.columns([1, 2])
    cod_in = c_id[0].text_input("Código", value=st.session_state.f["cod"])
    nom_in = c_id[1].text_input("Producto", value=st.session_state.f["nom"])

    c1, c2 = st.columns(2)
    in_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")

    m1, m2, m3 = st.columns([1, 1.2, 1.2])
    in_mar = m1.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    in_vusd = m2.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = m3.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # LOGICA 360 (PC STYLE)
    if in_vbs != st.session_state.f["vbs"]:
        st.session_state.f["vbs"], st.session_state.f["vusd"] = in_vbs, in_vbs / tasa_v
        st.session_state.f["cusd"] = st.session_state.f["vusd"] / (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()
    elif in_vusd != st.session_state.f["vusd"]:
        st.session_state.f["vusd"], st.session_state.f["vbs"] = in_vusd, in_vusd * tasa_v
        st.session_state.f["cusd"] = in_vusd / (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f["cusd"], st.session_state.f["cbs"] = in_cusd, in_cusd * tasa_v
        st.session_state.f["vusd"] = in_cusd * (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # Botones
    b1, b2 = st.columns(2)
    if b1.button("💾 GUARDAR CAMBIOS", type="primary"):
        datos = {"codigo": cod_in.upper(), "nombre": nom_in.upper(), "costo_bs": in_cbs, "costo_usd": in_cusd, "margen": in_mar, "venta_usd": in_vusd, "venta_bs": in_vbs}
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Producto actualizado!")
        st.rerun()
    if b2.button("🗑️ ELIMINAR"):
        supabase.table("productos").delete().eq("nombre", nom_in).execute()
        st.rerun()

# --- MODULO USUARIOS ---
with tab_usu:
    st.subheader("👥 Gestión de Personal")
    res_u = supabase.table("usuarios").select("*").execute()
    df_u = pd.DataFrame(res_u.data)
    
    with st.expander("➕ Agregar Nuevo Usuario"):
        u_nom = st.text_input("Nombre de Usuario")
        u_pass = st.text_input("Contraseña", type="password")
        u_rol = st.selectbox("Rol", ["Administrador", "Vendedor"])
        if st.button("CREAR USUARIO"):
            supabase.table("usuarios").insert({"usuario": u_nom, "clave": u_pass, "rol": u_rol}).execute()
            st.rerun()
    
    st.table(df_u[["usuario", "rol"]])
