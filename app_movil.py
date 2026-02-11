import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Tus llaves de siempre)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS (Colores exactos de tu PC)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    .stButton>button { border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ACTUAL ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- INVENTARIO ---
st.subheader("📦 INVENTARIO (PROTECCIÓN DE REPOSICIÓN)")

# Cargar datos para el selector
res_p = supabase.table("productos").select("*").order("nombre").execute()
df = pd.DataFrame(res_p.data)

st.camera_input("📷 ESCANEAR")
sel = st.selectbox("Buscar Producto", ["-- NUEVO --"] + sorted(df['nombre'].tolist() if not df.empty else []))

# Inicializar sesión para que los campos "se hablen"
if "form" not in st.session_state or sel != st.session_state.get("prev_sel"):
    f = df[df['nombre'] == sel].iloc[0] if sel != "-- NUEVO --" else None
    st.session_state.form = {
        "cbs": float(f['costo_bs']) if f is not None else 0.0,
        "cusd": float(f['costo_usd']) if f is not None else 0.0,
        "mar": float(f['margen']) if f is not None else 25.0,
        "vusd": float(f['venta_usd']) if f is not None else 0.0,
        "vbs": float(f['venta_bs']) if f is not None else 0.0,
        "cod": str(f['codigo']) if f is not None else "",
        "nom": str(f['nombre']) if f is not None else ""
    }
    st.session_state.prev_sel = sel

# --- GRILLA DE ENTRADA 360° (Como tu PC) ---
c_id1, c_id2 = st.columns([1, 2])
cod = c_id1.text_input("Código", value=st.session_state.form["cod"])
nom = c_id2.text_input("Producto", value=st.session_state.form["nom"])

col1, col2, col3 = st.columns(3)
# Escribe en cualquiera de estos:
n_cbs = col1.number_input("Costo Bs. (Fijo)", value=st.session_state.form["cbs"], format="%.2f")
n_cusd = col2.number_input("Costo $", value=st.session_state.form["cusd"], format="%.2f")
n_mar = col3.number_input("Margen %", value=st.session_state.form["mar"], format="%.2f")

col4, col5 = st.columns(2)
n_vusd = col4.number_input("Venta $", value=st.session_state.form["vusd"], format="%.2f")
n_vbs = col5.number_input("Venta Bs. (Móvil)", value=st.session_state.form["vbs"], format="%.2f")

# --- MOTOR DE CÁLCULO (Tu función recalcular()) ---
# Si tocas Costo Bs
if n_cbs != st.session_state.form["cbs"]:
    st.session_state.form["cbs"] = n_cbs
    st.session_state.form["cusd"] = n_cbs / tasa_v
    st.session_state.form["vusd"] = st.session_state.form["cusd"] * (1 + (st.session_state.form["mar"]/100))
    st.session_state.form["vbs"] = st.session_state.form["vusd"] * tasa_v
    st.rerun()

# Si tocas Venta $
elif n_vusd != st.session_state.form["vusd"]:
    st.session_state.form["vusd"] = n_vusd
    st.session_state.form["vbs"] = n_vusd * tasa_v
    if st.session_state.form["cusd"] > 0:
        st.session_state.form["mar"] = ((n_vusd / st.session_state.form["cusd"]) - 1) * 100
    st.rerun()

# Si tocas Venta Bs
elif n_vbs != st.session_state.form["vbs"]:
    st.session_state.form["vbs"] = n_vbs
    st.session_state.form["vusd"] = n_vbs / tasa_v
    if st.session_state.form["cusd"] > 0:
        st.session_state.form["mar"] = ((st.session_state.form.vusd / st.session_state.form["cusd"]) - 1) * 100
    st.rerun()

# Si tocas Margen
elif n_mar != st.session_state.form["mar"]:
    st.session_state.form["mar"] = n_mar
    st.session_state.form["vusd"] = st.session_state.form["cusd"] * (1 + (n_mar/100))
    st.session_state.form["vbs"] = st.session_state.form["vusd"] * tasa_v
    st.rerun()

# BOTONES
b1, b2 = st.columns(2)
if b1.button("💾 GUARDAR/ACTUALIZAR", type="primary"):
    datos = {
        "codigo": cod.upper(), "nombre": nom.upper(),
        "costo_bs": st.session_state.form["cbs"], "costo_usd": st.session_state.form["cusd"],
        "margen": st.session_state.form["mar"], "venta_usd": st.session_state.form["vusd"], "venta_bs": st.session_state.form["vbs"]
    }
    supabase.table("productos").upsert(datos).execute()
    st.success("¡Listo mano!")
    st.rerun()

st.divider()
st.subheader("📋 Inventario Registrado")
st.dataframe(df[["nombre", "costo_usd", "venta_usd", "venta_bs"]], use_container_width=True, hide_index=True)
