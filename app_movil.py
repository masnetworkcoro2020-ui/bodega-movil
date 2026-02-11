import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN Y ESTILOS (Tu configuración blindada)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

st.markdown("""
    <style>
    /* Colores de tu PC adaptados al móvil */
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    .stButton>button { border-radius: 12px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑA DE INVENTARIO ---
tab_tasa, tab_inv, tab_usu = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with tab_inv:
    st.subheader("🔄 Gestión Reactiva 360°")
    
    # Cargar datos actuales
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    
    st.camera_input("📷 ESCANEAR CÓDIGO")
    sel = st.selectbox("Selecciona para editar", ["-- NUEVO --"] + sorted(df['nombre'].tolist() if not df.empty else []))

    # --- LÓGICA DE RECALCULO AUTOMÁTICO ---
    if "form_data" not in st.session_state or sel != st.session_state.get("last_sel"):
        f = df[df['nombre'] == sel].iloc[0] if sel != "-- NUEVO --" else None
        st.session_state.form_data = {
            "cbs": float(f['costo_bs']) if f is not None else 0.0,
            "cusd": float(f['costo_usd']) if f is not None else 0.0,
            "margen": float(f['margen']) if f is not None else 25.0,
            "vbs": float(f['venta_bs']) if f is not None else 0.0,
            "vusd": float(f['venta_usd']) if f is not None else 0.0,
            "cod": str(f['codigo']) if f is not None else "",
            "nom": str(f['nombre']) if f is not None else ""
        }
        st.session_state.last_sel = sel

    # --- CAMPOS DE ENTRADA TOTAL ---
    st.session_state.form_data["cod"] = st.text_input("Código", value=st.session_state.form_data["cod"])
    st.session_state.form_data["nom"] = st.text_input("Producto", value=st.session_state.form_data["nom"])

    c1, c2 = st.columns(2)
    # COSTO BS (Escribe aquí y calcula USD)
    new_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.form_data["cbs"], format="%.2f")
    # COSTO USD (Escribe aquí y calcula BS)
    new_cusd = c2.number_input("Costo $", value=st.session_state.form_data["cusd"], format="%.2f")

    m1, m2 = st.columns(2)
    # MARGEN %
    new_margen = m1.number_input("Margen %", value=st.session_state.form_data["margen"], format="%.2f")
    # VENTA BS (Escribe aquí y calcula Margen y Venta $)
    new_vbs = m2.number_input("Venta Bs. (Móvil)", value=st.session_state.form_data["vbs"], format="%.2f")

    # --- MOTOR DE CÁLCULO 360° (Igual a tu recalcular()) ---
    if new_cbs != st.session_state.form_data["cbs"]:
        st.session_state.form_data["cbs"] = new_cbs
        st.session_state.form_data["cusd"] = new_cbs / tasa_v
        st.session_state.form_data["vusd"] = st.session_state.form_data["cusd"] * (1 + st.session_state.form_data["margen"]/100)
        st.session_state.form_data["vbs"] = st.session_state.form_data["vusd"] * tasa_v
        st.rerun()

    elif new_cusd != st.session_state.form_data["cusd"]:
        st.session_state.form_data["cusd"] = new_cusd
        st.session_state.form_data["cbs"] = new_cusd * tasa_v
        st.session_state.form_data["vusd"] = new_cusd * (1 + st.session_state.form_data["margen"]/100)
        st.session_state.form_data["vbs"] = st.session_state.form_data["vusd"] * tasa_v
        st.rerun()

    elif new_vbs != st.session_state.form_data["vbs"]:
        st.session_state.form_data["vbs"] = new_vbs
        st.session_state.form_data["vusd"] = new_vbs / tasa_v
        if st.session_state.form_data["cusd"] > 0:
            st.session_state.form_data["margen"] = ((st.session_state.form_data["vusd"] / st.session_state.form_data["cusd"]) - 1) * 100
        st.rerun()

    elif new_margen != st.session_state.form_data["margen"]:
        st.session_state.form_data["margen"] = new_margen
        st.session_state.form_data["vusd"] = st.session_state.form_data["cusd"] * (1 + new_margen/100)
        st.session_state.form_data["vbs"] = st.session_state.form_data["vusd"] * tasa_v
        st.rerun()

    st.warning(f"💡 Venta sugerida en dólares: **${st.session_state.form_data['vusd']:.2f}**")

    # --- ACCIONES ---
    col_b = st.columns(2)
    if col_b[0].button("💾 GUARDAR/ACTUALIZAR", type="primary"):
        d = {
            "codigo": st.session_state.form_data["cod"].upper(),
            "nombre": st.session_state.form_data["nom"].upper(),
            "costo_bs": st.session_state.form_data["cbs"],
            "costo_usd": st.session_state.form_data["cusd"],
            "margen": st.session_state.form_data["margen"],
            "venta_usd": st.session_state.form_data["vusd"],
            "venta_bs": st.session_state.form_data["vbs"]
        }
        supabase.table("productos").upsert(d).execute()
        st.success("¡Sincronizado!")
        st.rerun()

    if col_b[1].button("🗑️ ELIMINAR"):
        if sel != "-- NUEVO --":
            supabase.table("productos").delete().eq("nombre", sel).execute()
            st.rerun()

    st.divider()
    st.subheader("📋 Inventario Registrado")
    st.dataframe(df[["nombre", "costo_bs", "costo_usd", "margen", "venta_bs"]], use_container_width=True, hide_index=True)
