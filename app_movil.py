import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN Y CONEXIÓN
st.set_page_config(page_title="BODEGA PRO V2 - GESTIÓN 360", layout="centered")
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS DE COLORES ORIGINALES (Extraídos de tu imagen)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black !important; font-weight: bold !important; }
    .stButton>button { border-radius: 12px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TASA ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑAS ---
pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[1]:
    st.subheader("📦 Protección de Reposición 360°")
    
    # Cargar datos para el buscador
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    
    st.camera_input("📷 ESCANEAR CÓDIGO")
    opciones = ["-- NUEVO PRODUCTO --"] + sorted(df['nombre'].tolist() if not df.empty else [])
    sel = st.selectbox("Selecciona para editar", opciones)
    
    # --- FORMULARIO CON TU LÓGICA DE RECALCULAR() ---
    with st.container():
        fila = df[df['nombre'] == sel].iloc[0] if sel != "-- NUEVO PRODUCTO --" else None
        
        col_id = st.columns(2)
        cod = col_id[0].text_input("Código", value=str(fila['codigo']) if fila is not None else "")
        nom = col_id[1].text_input("Producto", value=str(fila['nombre']) if fila is not None else "")
        
        # Inicializamos variables para los cálculos
        if "c_bs" not in st.session_state or sel != st.session_state.get("last_sel"):
            st.session_state.c_bs = float(fila['costo_bs']) if fila is not None else 0.0
            st.session_state.c_usd = float(fila['costo_usd']) if fila is not None else 0.0
            st.session_state.margen = float(fila['margen']) if fila is not None else 25.0
            st.session_state.v_bs = float(fila['venta_bs']) if fila is not None else 0.0
            st.session_state.v_usd = float(fila['venta_usd']) if fila is not None else 0.0
            st.session_state.last_sel = sel

        # FILA 1: COSTOS
        c1, c2 = st.columns(2)
        new_cbs = c1.number_input("Costo Bs. (Fijo)", value=st.session_state.c_bs, format="%.2f")
        new_cusd = c2.number_input("Costo $", value=st.session_state.c_usd, format="%.2f")
        
        # FILA 2: MARGEN Y VENTAS
        m1, m2 = st.columns(2)
        new_margen = m1.number_input("Margen %", value=st.session_state.margen, format="%.2f")
        new_vbs = m2.number_input("Venta Bs. (Móvil)", value=st.session_state.v_bs, format="%.2f")
        
        # --- IMPLEMENTACIÓN DE TU LÓGICA MATEMÁTICA ---
        # Si cambiaste Costo Bs
        if new_cbs != st.session_state.c_bs:
            st.session_state.c_bs = new_cbs
            st.session_state.c_usd = new_cbs / tasa_v
            st.session_state.v_usd = st.session_state.c_usd * (1 + (st.session_state.margen/100))
            st.session_state.v_bs = st.session_state.v_usd * tasa_v
            st.rerun()
            
        # Si cambiaste Venta Bs (Manual)
        elif new_vbs != st.session_state.v_bs:
            st.session_state.v_bs = new_vbs
            st.session_state.v_usd = new_vbs / tasa_v
            if st.session_state.c_usd > 0:
                st.session_state.margen = ((st.session_state.v_usd / st.session_state.c_usd) - 1) * 100
            st.rerun()

        # Si cambiaste Margen
        elif new_margen != st.session_state.margen:
            st.session_state.margen = new_margen
            st.session_state.v_usd = st.session_state.c_usd * (1 + (new_margen/100))
            st.session_state.v_bs = st.session_state.v_usd * tasa_v
            st.rerun()

        st.write(f"💵 Venta sugerida: **${st.session_state.v_usd:.2f} USD**")

        # --- BOTONES DE ACCIÓN ---
        b1, b2 = st.columns(2)
        if b1.button("💾 GUARDAR/ACTUALIZAR", type="primary"):
            datos = {
                "codigo": cod.upper(), "nombre": nom.upper(),
                "costo_bs": st.session_state.c_bs, "costo_usd": st.session_state.c_usd,
                "margen": st.session_state.margen, "venta_usd": st.session_state.v_usd, "venta_bs": st.session_state.v_bs
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Sincronizado!")
            st.rerun()
        
        if b2.button("🗑️ ELIMINAR"):
            if sel != "-- NUEVO PRODUCTO --":
                supabase.table("productos").delete().eq("nombre", sel).execute()
                st.rerun()

    st.divider()
    st.subheader("📋 Inventario Registrado")
    st.dataframe(df[["nombre", "costo_bs", "costo_usd", "margen", "venta_bs"]], use_container_width=True, hide_index=True)
