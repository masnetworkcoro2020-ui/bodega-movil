import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Tus llaves maestras)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS DE COLORES (PC Style)
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; background-color: #1f538d; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑA INVENTARIO ---
tab_tasa, tab_inv, tab_usu = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with tab_inv:
    st.subheader("🔄 Gestión 360° Completa")
    
    st.camera_input("📷 ESCANEAR")
    
    # Usamos session_state para que los cambios sean instantáneos como en la PC
    if "prod_data" not in st.session_state:
        st.session_state.prod_data = {"c_bs": 0.0, "c_usd": 0.0, "margen": 25.0, "v_bs": 0.0, "v_usd": 0.0}

    with st.container():
        cod = st.text_input("Código")
        nom = st.text_input("Producto")
        
        # FILA DE COSTOS (Aquí está el corazón)
        col1, col2 = st.columns(2)
        
        # Entrada de Costo Bs
        c_bs_input = col1.number_input("Costo Bs. (Fijo)", value=st.session_state.prod_data["c_bs"], format="%.2f", key="c_bs")
        
        # Entrada de Costo $ (Lo que faltaba)
        c_usd_input = col2.number_input("Costo $", value=st.session_state.prod_data["c_usd"], format="%.2f", key="c_usd")
        
        # FILA DE VENTA Y MARGEN
        col3, col4 = st.columns(2)
        margen_input = col3.number_input("Margen %", value=st.session_state.prod_data["margen"], format="%.2f")
        v_bs_input = col4.number_input("Venta Bs. (Móvil)", value=st.session_state.prod_data["v_bs"], format="%.2f")

        # --- LÓGICA DE RECALCULO 360° ---
        
        # 1. Si mueves el Costo $ (NUEVO)
        if c_usd_input != st.session_state.prod_data["c_usd"]:
            st.session_state.prod_data["c_usd"] = c_usd_input
            st.session_state.prod_data["c_bs"] = c_usd_input * tasa_v
            st.session_state.prod_data["v_usd"] = c_usd_input * (1 + (st.session_state.prod_data["margen"]/100))
            st.session_state.prod_data["v_bs"] = st.session_state.prod_data["v_usd"] * tasa_v
            st.rerun()

        # 2. Si mueves el Costo Bs
        elif c_bs_input != st.session_state.prod_data["c_bs"]:
            st.session_state.prod_data["c_bs"] = c_bs_input
            st.session_state.prod_data["c_usd"] = c_bs_input / tasa_v
            st.session_state.prod_data["v_usd"] = st.session_state.prod_data["c_usd"] * (1 + (st.session_state.prod_data["margen"]/100))
            st.session_state.prod_data["v_bs"] = st.session_state.prod_data["v_usd"] * tasa_v
            st.rerun()

        # 3. Si mueves la Venta Bs
        elif v_bs_input != st.session_state.prod_data["v_bs"]:
            st.session_state.prod_data["v_bs"] = v_bs_input
            v_usd_temp = v_bs_input / tasa_v
            if st.session_state.prod_data["c_usd"] > 0:
                st.session_state.prod_data["margen"] = ((v_usd_temp / st.session_state.prod_data["c_usd"]) - 1) * 100
            st.session_state.prod_data["v_usd"] = v_usd_temp
            st.rerun()

        st.info(f"📊 **Resumen:** Venta ${st.session_state.prod_data['v_usd']:.2f} | Margen: {st.session_state.prod_data['margen']:.2f}%")

        if st.button("💾 GUARDAR PRODUCTO"):
            datos = {
                "codigo": cod.upper(), "nombre": nom.upper(),
                "costo_bs": st.session_state.prod_data["c_bs"],
                "costo_usd": st.session_state.prod_data["c_usd"],
                "margen": round(st.session_state.prod_data["margen"], 2),
                "venta_usd": round(st.session_state.prod_data["v_usd"], 2),
                "venta_bs": round(st.session_state.prod_data["v_bs"], 2)
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Sincronizado!")
            st.rerun()

    st.divider()
    # Tabla de abajo para ver que todo cuadre
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    st.dataframe(df[["nombre", "costo_usd", "venta_usd", "venta_bs"]], use_container_width=True, hide_index=True)
