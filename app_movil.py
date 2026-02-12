import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Tus credenciales blindadas)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS (Colores originales de tu PC)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    .stButton>button { border-radius: 12px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA (ID:1) ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑA INVENTARIO ---
tab_tasa, tab_inv, tab_usu = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with tab_inv:
    st.subheader("📦 REPLICACIÓN 360° (PC STYLE)")
    
    # Session State para manejar el recalculo circular
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0}

    st.camera_input("📷 ESCANEAR")
    
    with st.container():
        cod = st.text_input("Código")
        nom = st.text_input("Producto")
        
        # FILA 1: COSTOS
        c1, c2 = st.columns(2)
        n_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.f["cbs"], format="%.2f")
        n_cusd = c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
        
        # FILA 2: MARGEN Y VENTAS
        m1, m2, m3 = st.columns([1, 1.2, 1.2])
        n_mar = m1.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
        n_vusd = m2.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
        n_vbs = m3.number_input("Venta Bs. (Móvil)", value=st.session_state.f["vbs"], format="%.2f")

        # --- MOTOR DE CÁLCULO 360° (Replicando tu recalcular()) ---
        m = n_mar / 100

        # A. Si mueves COSTO BS (Hacia adelante)
        if n_cbs != st.session_state.f["cbs"]:
            st.session_state.f["cbs"] = n_cbs
            st.session_state.f["cusd"] = n_cbs / tasa_v
            st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + m)
            st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
            st.rerun()

        # B. Si mueves COSTO $ (Hacia adelante)
        elif n_cusd != st.session_state.f["cusd"]:
            st.session_state.f["cusd"] = n_cusd
            st.session_state.f["cbs"] = n_cusd * tasa_v
            st.session_state.f["vusd"] = n_cusd * (1 + m)
            st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
            st.rerun()

        # C. Si mueves VENTA BS (Hacia atrás)
        elif n_vbs != st.session_state.f["vbs"]:
            st.session_state.f["vbs"] = n_vbs
            st.session_state.f["vusd"] = n_vbs / tasa_v
            if st.session_state.f["cusd"] > 0:
                st.session_state.f["mar"] = ((st.session_state.f["vusd"] / st.session_state.f["cusd"]) - 1) * 100
            st.rerun()

        # D. Si mueves VENTA $ (Hacia atrás)
        elif n_vusd != st.session_state.f["vusd"]:
            st.session_state.f["vusd"] = n_vusd
            st.session_state.f["vbs"] = n_vusd * tasa_v
            if st.session_state.f["cusd"] > 0:
                st.session_state.f["mar"] = ((n_vusd / st.session_state.f["cusd"]) - 1) * 100
            st.rerun()

        # E. Si mueves MARGEN %
        elif n_mar != st.session_state.f["mar"]:
            st.session_state.f["mar"] = n_mar
            st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (n_mar/100))
            st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
            st.rerun()

        # BOTONES DE ACCIÓN
        col_btn = st.columns(2)
        if col_btn[0].button("💾 GUARDAR/ACTUALIZAR", type="primary"):
            datos = {
                "codigo": cod.upper(), "nombre": nom.upper(),
                "costo_bs": st.session_state.f["cbs"], "costo_usd": st.session_state.f["cusd"],
                "margen": st.session_state.f["mar"], "venta_usd": st.session_state.f["vusd"], "venta_bs": st.session_state.f["vbs"]
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Sincronizado con éxito!")
            st.rerun()

        if col_btn[1].button("🗑️ ELIMINAR"):
            if cod:
                supabase.table("productos").delete().eq("codigo", cod.upper()).execute()
                st.rerun()

    st.divider()
    # Listado inferior para control visual
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    st.dataframe(df[["nombre", "costo_bs", "venta_bs"]], use_container_width=True, hide_index=True)
