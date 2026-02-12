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
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- LÓGICA DE CARGA DE DATOS ---
if "f" not in st.session_state:
    st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[1]:
    st.subheader("📦 Gestión Pro 360°")
    
    # BUSCADOR (Igual que en la PC para editar)
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df_lista = pd.DataFrame(res_p.data)
    
    opciones_busqueda = ["-- NUEVO PRODUCTO --"] + sorted(df_lista['nombre'].tolist() if not df_lista.empty else [])
    seleccion = st.selectbox("🔍 Buscar para Editar o Eliminar", opciones_busqueda)

    # Si seleccionas algo, cargamos los datos al session_state
    if seleccion != "-- NUEVO PRODUCTO --" and seleccion != st.session_state.get("last_sel"):
        prod = df_lista[df_lista['nombre'] == seleccion].iloc[0]
        st.session_state.f = {
            "cbs": float(prod['costo_bs']), "cusd": float(prod['costo_usd']),
            "mar": float(prod['margen']), "vbs": float(prod['venta_bs']),
            "vusd": float(prod['venta_usd']), "cod": str(prod['codigo']), "nom": str(prod['nombre'])
        }
        st.session_state.last_sel = seleccion
    elif seleccion == "-- NUEVO PRODUCTO --" and st.session_state.get("last_sel") != "-- NUEVO PRODUCTO --":
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}
        st.session_state.last_sel = "-- NUEVO PRODUCTO --"

    with st.container():
        # Identificación
        c_id = st.columns([1, 2])
        cod_in = c_id[0].text_input("Código", value=st.session_state.f["cod"])
        nom_in = c_id[1].text_input("Producto", value=st.session_state.f["nom"])

        # FILA 1: COSTOS
        c1, c2 = st.columns(2)
        in_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.f["cbs"], format="%.2f")
        in_cusd = c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")

        # FILA 2: MARGEN Y VENTAS
        m1, m2, m3 = st.columns([1, 1.2, 1.2])
        in_mar = m1.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
        in_vusd = m2.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
        in_vbs = m3.number_input("Venta Bs. (Móvil)", value=st.session_state.f["vbs"], format="%.2f")

        # --- MOTOR 360° TOTAL (Tu lógica de inventario.py) ---
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
        elif in_mar != st.session_state.f["mar"]:
            st.session_state.f["mar"] = in_mar
            st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (in_mar/100))
            st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
            st.rerun()

        # BOTONES
        b1, b2 = st.columns(2)
        if b1.button("💾 GUARDAR / EDITAR", type="primary"):
            datos = {
                "codigo": cod_in.upper(), "nombre": nom_in.upper(),
                "costo_bs": st.session_state.f["cbs"], "costo_usd": st.session_state.f["cusd"],
                "margen": st.session_state.f["mar"], "venta_usd": st.session_state.f["vusd"], "venta_bs": st.session_state.f["vbs"]
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Sincronizado!")
            st.rerun()
            
        if b2.button("🗑️ ELIMINAR PRODUCTO"):
            if nom_in:
                supabase.table("productos").delete().eq("nombre", nom_in).execute()
                st.warning(f"Producto {nom_in} eliminado.")
                st.rerun()

    st.divider()
    st.dataframe(df_lista[["nombre", "venta_bs", "margen"]], use_container_width=True, hide_index=True)
