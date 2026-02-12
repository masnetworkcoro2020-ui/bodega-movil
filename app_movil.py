import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Tus credenciales blindadas)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS (Colores de la PC: Amarillo para Costo Bs, Gris para Costo $, Verde para Venta Bs)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black !important; font-weight: bold !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta $")) input { background-color: #d6eaf8 !important; color: black !important; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; background-color: #1f538d; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ACTUAL (ID:1 como en tu PC) ---
try:
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0
except:
    tasa_v = 40.0

# --- PESTAÑAS DEL SISTEMA ---
pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

# PESTAÑA 1: TASA (Para que la actualices desde el tlf)
with pestanas[0]:
    st.subheader("Configuración de Tasa")
    nueva_tasa = st.number_input("Tasa BCV / Paralelo", value=tasa_v, format="%.2f")
    if st.button("ACTUALIZAR TASA"):
        supabase.table("ajustes").update({"valor": nueva_tasa}).eq("id", 1).execute()
        st.success(f"Tasa actualizada a {nueva_tasa}")
        st.rerun()

# PESTAÑA 2: INVENTARIO (El corazón 360°)
with pestanas[1]:
    st.subheader("Gestión de Inventario 360°")
    
    # Session State para el motor circular (Evita que se borren los datos al recalcular)
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

    st.camera_input("📷 ESCANEAR CÓDIGO")

    with st.container():
        # Identificación
        c_id = st.columns([1, 2])
        cod_input = c_id[0].text_input("Código", value=st.session_state.f["cod"])
        nom_input = c_id[1].text_input("Producto", value=st.session_state.f["nom"])

        # FILA 1: COSTOS
        c1, c2 = st.columns(2)
        in_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.f["cbs"], format="%.2f")
        in_cusd = c2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")

        # FILA 2: MARGEN Y VENTAS
        m1, m2, m3 = st.columns([1, 1.2, 1.2])
        in_mar = m1.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")
        in_vusd = m2.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
        in_vbs = m3.number_input("Venta Bs. (Móvil)", value=st.session_state.f["vbs"], format="%.2f")

        # --- MOTOR DE RECALCULO 360° (Lógica Original de inventario.py) ---
        
        # 1. Ajuste por Venta Bs (Hacia atrás)
        if in_vbs != st.session_state.f["vbs"]:
            st.session_state.f["vbs"] = in_vbs
            st.session_state.f["vusd"] = in_vbs / tasa_v
            st.session_state.f["cusd"] = st.session_state.f["vusd"] / (1 + (st.session_state.f["mar"]/100))
            st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
            st.rerun()

        # 2. Ajuste por Venta $ (Hacia atrás)
        elif in_vusd != st.session_state.f["vusd"]:
            st.session_state.f["vusd"] = in_vusd
            st.session_state.f["vbs"] = in_vusd * tasa_v
            st.session_state.f["cusd"] = in_vusd / (1 + (st.session_state.f["mar"]/100))
            st.session_state.f["cbs"] = st.session_state.f["cusd"] * tasa_v
            st.rerun()

        # 3. Ajuste por Costo Bs (Hacia adelante)
        elif in_cbs != st.session_state.f["cbs"]:
            st.session_state.f["cbs"] = in_cbs
            st.session_state.f["cusd"] = in_cbs / tasa_v
            st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (st.session_state.f["mar"]/100))
            st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
            st.rerun()

        # 4. Ajuste por Costo $ (Hacia adelante)
        elif in_cusd != st.session_state.f["cusd"]:
            st.session_state.f["cusd"] = in_cusd
            st.session_state.f["cbs"] = in_cusd * tasa_v
            st.session_state.f["vusd"] = in_cusd * (1 + (st.session_state.f["mar"]/100))
            st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
            st.rerun()

        # 5. Ajuste por Margen
        elif in_mar != st.session_state.f["mar"]:
            st.session_state.f["mar"] = in_mar
            st.session_state.f["vusd"] = st.session_state.f["cusd"] * (1 + (in_mar/100))
            st.session_state.f["vbs"] = st.session_state.f["vusd"] * tasa_v
            st.rerun()

        # BOTONES DE ACCIÓN
        b1, b2 = st.columns(2)
        if b1.button("💾 GUARDAR / ACTUALIZAR"):
            datos = {
                "codigo": cod_input.upper(), "nombre": nom_input.upper(),
                "costo_bs": st.session_state.f["cbs"], "costo_usd": st.session_state.f["cusd"],
                "margen": st.session_state.f["mar"], "venta_usd": st.session_state.f["vusd"], "venta_bs": st.session_state.f["vbs"]
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Producto Guardado!")
            st.rerun()
            
        if b2.button("🗑️ ELIMINAR"):
            if cod_input:
                supabase.table("productos").delete().eq("codigo", cod_input.upper()).execute()
                st.rerun()

    st.divider()
    # TABLA DE REGISTROS (Para consulta rápida abajo)
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    if not df.empty:
        st.dataframe(df[["nombre", "costo_usd", "venta_usd", "venta_bs"]], use_container_width=True, hide_index=True)

# PESTAÑA 3: USUARIOS (Placeholder)
with pestanas[2]:
    st.subheader("Gestión de Usuarios")
    st.info("Módulo de seguridad en desarrollo...")
