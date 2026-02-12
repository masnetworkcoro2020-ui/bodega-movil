import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Blindada)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS DE TU PC (Amarillo Costo, Verde Venta)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta $")) input { background-color: #d6eaf8 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. TASA (ID:1)
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

with st.container():
    st.subheader("🛠️ Calculadora 360° Pro")
    
    # Session State para manejar la reactividad circular
    if "val" not in st.session_state:
        st.session_state.val = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0}

    # FILA 1: IDENTIFICACIÓN
    col_id1, col_id2 = st.columns([1, 2])
    cod = col_id1.text_input("Código")
    nom = col_id2.text_input("Producto")

    # FILA 2: COSTOS
    c1, c2 = st.columns(2)
    in_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.val["cbs"], format="%.2f")
    in_cusd = c2.number_input("Costo $", value=st.session_state.val["cusd"], format="%.2f")

    # FILA 3: MARGEN Y VENTAS
    m1, m2, m3 = st.columns([1, 1.5, 1.5])
    in_mar = m1.number_input("Margen %", value=st.session_state.val["mar"], format="%.1f")
    in_vusd = m2.number_input("Venta $", value=st.session_state.val["vusd"], format="%.2f")
    in_vbs = m3.number_input("Venta Bs. (Móvil)", value=st.session_state.val["vbs"], format="%.2f")

    # --- MOTOR DE RECALCULO 360° (LÓGICA DEL ORIGINAL) ---
    
    # 1. Si mueves Venta Bs (Hacia atrás)
    if in_vbs != st.session_state.val["vbs"]:
        st.session_state.val["vbs"] = in_vbs
        st.session_state.val["vusd"] = in_vbs / tasa_v
        if st.session_state.val["cusd"] > 0:
            st.session_state.val["mar"] = ((st.session_state.val["vusd"] / st.session_state.val["cusd"]) - 1) * 100
        st.rerun()

    # 2. Si mueves Venta $ (Hacia atrás)
    elif in_vusd != st.session_state.val["vusd"]:
        st.session_state.val["vusd"] = in_vusd
        st.session_state.val["vbs"] = in_vusd * tasa_v
        if st.session_state.val["cusd"] > 0:
            st.session_state.val["mar"] = ((in_vusd / st.session_state.val["cusd"]) - 1) * 100
        st.rerun()

    # 3. Si mueves Costo Bs (Hacia adelante)
    elif in_cbs != st.session_state.val["cbs"]:
        st.session_state.val["cbs"] = in_cbs
        st.session_state.val["cusd"] = in_cbs / tasa_v
        st.session_state.val["vusd"] = st.session_state.val["cusd"] * (1 + (st.session_state.val["mar"]/100))
        st.session_state.val["vbs"] = st.session_state.val["vusd"] * tasa_v
        st.rerun()

    # 4. Si mueves Costo $ (Hacia adelante)
    elif in_cusd != st.session_state.val["cusd"]:
        st.session_state.val["cusd"] = in_cusd
        st.session_state.val["cbs"] = in_cusd * tasa_v
        st.session_state.val["vusd"] = in_cusd * (1 + (st.session_state.val["mar"]/100))
        st.session_state.val["vbs"] = st.session_state.val["vusd"] * tasa_v
        st.rerun()

    # 5. Si mueves el Margen
    elif in_mar != st.session_state.val["mar"]:
        st.session_state.val["mar"] = in_mar
        st.session_state.val["vusd"] = st.session_state.val["cusd"] * (1 + (in_mar/100))
        st.session_state.val["vbs"] = st.session_state.val["vusd"] * tasa_v
        st.rerun()

    # BOTÓN DE GUARDADO
    if st.button("💾 REGISTRAR CAMBIOS 360°"):
        datos = {
            "codigo": cod.upper(), "nombre": nom.upper(),
            "costo_bs": st.session_state.val["cbs"], "costo_usd": st.session_state.val["cusd"],
            "margen": st.session_state.val["mar"], "venta_usd": st.session_state.val["vusd"], "venta_bs": st.session_state.val["vbs"]
        }
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Sincronizado!")
        st.rerun()

st.divider()
st.subheader("📋 Inventario Actual")
res_p = supabase.table("productos").select("*").order("nombre").execute()
df = pd.DataFrame(res_p.data)
st.dataframe(df[["nombre", "costo_usd", "venta_usd", "venta_bs"]], use_container_width=True, hide_index=True)
