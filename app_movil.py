import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Blindada)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. CONFIGURACIÓN Y ESTILOS MÓVIL
st.set_page_config(page_title="BODEGA MOVIL", layout="centered")
st.markdown("""
    <style>
    .stNumberInput input, .stTextInput input { height: 50px !important; font-size: 18px !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black; font-weight: bold; }
    .stButton>button { width: 100%; height: 55px !important; border-radius: 12px; font-weight: bold; }
    .user-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #1f538d; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["💰 TASA", "📦 INV", "👥 USUARIOS"])

# --- PESTAÑA TASA ---
with tab1:
    st.subheader("Ajuste de Tasa")
    nt = st.number_input("Tasa Hoy:", value=tasa_v, format="%.2f")
    if st.button("💾 ACTUALIZAR TASA"):
        supabase.table("ajustes").update({"valor": nt}).eq("id", 1).execute()
        st.success("Tasa Actualizada")
        st.rerun()

# --- PESTAÑA INVENTARIO (CON ESCANEO Y MOTOR 360) ---
with tab2:
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
    
    # --- ESCANEO ---
    foto_codigo = st.camera_input("📷 ESCANEAR CÓDIGO")
    if foto_codigo:
        st.info("Código capturado. (Aquí podrías integrar un decodificador si fuera necesario)")

    # Buscador para editar
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    opciones = ["-- NUEVO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    seleccion = st.selectbox("🔍 Buscar Producto:", opciones)

    if seleccion != "-- NUEVO --" and seleccion != st.session_state.get("last_sel"):
        p = df_lista[df_lista['nombre'] == seleccion].iloc[0]
        st.session_state.f = {"cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']), "mar": float(p['margen']), "vbs": float(p['venta_bs']), "vusd": float(p['venta_usd']), "cod": str(p['codigo']), "nom": str(p['nombre'])}
        st.session_state.last_sel = seleccion
    elif seleccion == "-- NUEVO --" and st.session_state.get("last_sel") != "-- NUEVO --":
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
        st.session_state.last_sel = "-- NUEVO --"

    # Campos
    cod_in = st.text_input("Código:", value=st.session_state.f["cod"])
    nom_in = st.text_input("Producto:", value=st.session_state.f["nom"])
    
    c1, c2 = st.columns(2)
    in_cbs = c1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    
    in_mar = st.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    
    v1, v2 = st.columns(2)
    in_vusd = v1.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = v2.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # LÓGICA 360 CIRCULAR (PC ORIGINAL)
    if in_vbs != st.session_state.f["vbs"]:
        st.session_state.f["vbs"] = in_vbs
        st.session_state.f["vusd"] = in_vbs / tasa_v
        st.session_state.f["cusd"] = st.session_state.f["vusd"] / (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()
    elif in_vusd != st.session_state.f["vusd"]:
        st.session_state.f["vusd"] = in_vusd
        st.session_state.f["vbs"] = in_vusd * tasa_v
        st.session_state.f["cusd"] = in_vusd / (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f["cusd"] = in_cusd
        st.session_state.f["cbs"] = in_cusd * tasa_v
        st.session_state.f["vusd"] = in_cusd * (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    if st.button("💾 GUARDAR"):
        datos = {"codigo": cod_in.upper(), "nombre": nom_in.upper(), "costo_bs": in_cbs, "costo_usd": in_cusd, "margen": in_mar, "venta_usd": in_vusd, "venta_bs": in_vbs}
        supabase.table("productos").upsert(datos).execute()
        st.success("Guardado")
        st.rerun()

# --- PESTAÑA USUARIOS ---
with tab3:
    st.subheader("👥 Usuarios")
    with st.expander("➕ Crear Nuevo"):
        nu, np = st.text_input("Usuario:"), st.text_input("Clave:", type="password")
        nr = st.selectbox("Rol:", ["Administrador", "Vendedor"])
        if st.button("REGISTRAR"):
            supabase.table("usuarios").insert({"usuario": nu, "clave": np, "rol": nr}).execute()
            st.rerun()

    res_u = supabase.table("usuarios").select("*").execute()
    for u in res_u.data:
        st.markdown(f'<div class="user-card"><b>{u["usuario"]}</b> ({u["rol"]})</div>', unsafe_allow_html=True)
        if st.button(f"🗑️ Eliminar {u['usuario']}", key=u['usuario']):
            supabase.table("usuarios").delete().eq("usuario", u['usuario']).execute()
            st.rerun()
