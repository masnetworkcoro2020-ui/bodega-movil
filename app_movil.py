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
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black !important; font-weight: bold !important; }
    .stButton>button { border-radius: 12px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑA INVENTARIO ---
tab_tasa, tab_inv, tab_usu = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with tab_inv:
    st.subheader("🔄 Gestión Reactiva 360°")
    
    # Session State para que los campos "reaccionen" entre ellos
    if "f_data" not in st.session_state:
        st.session_state.f_data = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0}

    st.camera_input("📷 ESCANEAR")
    
    with st.container():
        cod = st.text_input("Código")
        nom = st.text_input("Producto")
        
        # FILA 1: COSTOS (Ambos manuales)
        col1, col2 = st.columns(2)
        n_cbs = col1.number_input("Costo Bs. (Fijo)", value=st.session_state.f_data["cbs"], format="%.2f")
        n_cusd = col2.number_input("Costo $", value=st.session_state.f_data["cusd"], format="%.2f")
        
        # FILA 2: MARGEN Y VENTA
        col3, col4 = st.columns(2)
        n_mar = col3.number_input("Margen %", value=st.session_state.f_data["mar"], format="%.2f")
        n_vbs = col4.number_input("Venta Bs. (Móvil)", value=st.session_state.f_data["vbs"], format="%.2f")

        # --- LÓGICA DE RECALCULO 360° (Tu función recalcular()) ---
        
        # A. Si escribes en COSTO BS manual:
        if n_cbs != st.session_state.f_data["cbs"]:
            st.session_state.f_data["cbs"] = n_cbs
            st.session_state.f_data["cusd"] = n_cbs / tasa_v
            st.session_state.f_data["vusd"] = st.session_state.f_data["cusd"] * (1 + (st.session_state.f_data["mar"]/100))
            st.session_state.f_data["vbs"] = st.session_state.f_data["vusd"] * tasa_v
            st.rerun()

        # B. Si escribes en COSTO $ manual:
        elif n_cusd != st.session_state.f_data["cusd"]:
            st.session_state.f_data["cusd"] = n_cusd
            st.session_state.f_data["cbs"] = n_cusd * tasa_v
            st.session_state.f_data["vusd"] = n_cusd * (1 + (st.session_state.f_data["mar"]/100))
            st.session_state.f_data["vbs"] = st.session_state.f_data["vusd"] * tasa_v
            st.rerun()

        # C. Si escribes en VENTA BS manual:
        elif n_vbs != st.session_state.f_data["vbs"]:
            st.session_state.f_data["vbs"] = n_vbs
            v_usd_act = n_vbs / tasa_v
            if st.session_state.f_data["cusd"] > 0:
                st.session_state.f_data["mar"] = ((v_usd_act / st.session_state.f_data["cusd"]) - 1) * 100
            st.session_state.f_data["vusd"] = v_usd_act
            st.rerun()

        st.info(f"📊 **Venta USD:** ${st.session_state.f_data['vusd']:.2f} | **Margen:** {st.session_state.f_data['mar']:.2f}%")

        if st.button("💾 GUARDAR PRODUCTO"):
            datos = {
                "codigo": cod.upper(), "nombre": nom.upper(),
                "costo_bs": st.session_state.f_data["cbs"],
                "costo_usd": st.session_state.f_data["cusd"],
                "margen": round(st.session_state.f_data["mar"], 2),
                "venta_usd": round(st.session_state.f_data["vusd"], 2),
                "venta_bs": round(st.session_state.f_data["vbs"], 2)
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Sincronizado!")
            st.rerun()

    st.divider()
    # Lista de consulta abajo
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    st.dataframe(df[["nombre", "costo_bs", "venta_bs"]], use_container_width=True, hide_index=True)
