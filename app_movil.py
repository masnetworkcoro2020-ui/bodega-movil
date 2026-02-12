import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS (Colores de la PC)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta $")) input { background-color: #d6eaf8 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. TASA
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# Session State para el Motor Circular
if "f" not in st.session_state:
    st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0}

with st.container():
    st.subheader("🔄 Calculadora Circular 360°")
    
    col_id = st.columns([1, 2])
    cod = col_id[0].text_input("Código")
    nom = col_id[1].text_input("Producto")

    # FILA 1: COSTOS
    c1, c2 = st.columns(2)
    in_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")

    # FILA 2: MARGEN Y VENTAS
    m1, m2, m3 = st.columns([1, 1.2, 1.2])
    in_mar = m1.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
    in_vusd = m2.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = m3.number_input("Venta Bs. (Móvil)", value=st.session_state.f["vbs"], format="%.2f")

    # --- MOTOR DE RECALCULO 360° TOTAL ---
    
    # 1. SI TOCAS VENTA BS (Calcula todo hacia atrás)
    if in_vbs != st.session_state.f["vbs"]:
        st.session_state.f["vbs"] = in_vbs
        st.session_state.f["vusd"] = in_vbs / tasa_v
        # Costo USD = Venta USD / (1 + Margen)
        st.session_state.f["cusd"] = st.session_state.f["vusd"] / (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()

    # 2. SI TOCAS VENTA $ (Calcula todo hacia atrás)
    elif in_vusd != st.session_state.f["vusd"]:
        st.session_state.f["vusd"] = in_vusd
        st.session_state.f["vbs"] = in_vusd * tasa_v
        # Costo USD = Venta USD / (1 + Margen)
        st.session_state.f["cusd"] = in_vusd / (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
        st.rerun()

    # 3. SI TOCAS COSTO $ (Calcula todo hacia adelante)
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f["cusd"] = in_cusd
        st.session_state.f["cbs"] = in_cusd * tasa_v
        st.session_state.f["vusd"] = in_cusd * (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # 4. SI TOCAS COSTO BS (Calcula todo hacia adelante)
    elif in_cbs != st.session_state.f["cbs"]:
        st.session_state.f["cbs"] = in_cbs
        st.session_state.f["cusd"] = in_cbs / tasa_v
        st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (st.session_state.f["mar"]/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    # 5. SI TOCAS EL MARGEN % (Recalcula Ventas manteniendo Costos)
    elif in_mar != st.session_state.f["mar"]:
        st.session_state.f["mar"] = in_mar
        st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (in_mar/100))
        st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
        st.rerun()

    if st.button("💾 REGISTRAR PRODUCTO"):
        # Lógica de guardado...
        st.success("Guardado en 360°")
