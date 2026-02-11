import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS DE COLORES ORIGINALES
st.markdown("""
    <style>
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black !important; }
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; background-color: #1f538d; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- TASA ACTUAL ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑAS ---
pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[1]:
    st.subheader("🛠️ Gestión 360° Sin Redundancia")
    
    st.camera_input("📷 ESCANEAR")
    
    # Contenedor principal de datos
    with st.container():
        cod = st.text_input("Código")
        nom = st.text_input("Producto")
        
        # Fila de Costos
        col1, col2 = st.columns(2)
        c_bs = col1.number_input("Costo Bs. (Fijo)", value=0.0, format="%.2f")
        c_usd = col2.number_input("Costo $", value=0.0, format="%.2f")
        
        # Fila de Venta y Margen (Sin selectores raros)
        col3, col4 = st.columns(2)
        margen = col3.number_input("Margen %", value=25.0)
        v_bs = col4.number_input("Venta Bs. (Manual)", value=0.0, format="%.2f")
        
        # --- LÓGICA DE CÁLCULO AUTOMÁTICO (PC STYLE) ---
        # Si pones el precio en Bs, calculamos el Margen real
        if v_bs > 0 and c_usd > 0:
            v_usd_calc = v_bs / tasa_v
            margen_real = ((v_usd_calc / c_usd) - 1) * 100
            st.info(f"📈 Margen Real: {margen_real:.2f}% | Venta: ${v_usd_calc:.2f}")
        # Si prefieres usar el Margen prefijado
        elif margen > 0 and c_usd > 0 and v_bs == 0:
            v_usd_sug = c_usd * (1 + (margen/100))
            v_bs_sug = v_usd_sug * tasa_v
            st.success(f"💡 Sugerido: Bs. {v_bs_sug:.2f} (${v_usd_sug:.2f})")

        if st.button("💾 GUARDAR CAMBIOS"):
            # Si escribiste en Venta Bs, usamos eso. Si no, usamos el margen.
            final_vbs = v_bs if v_bs > 0 else (c_usd * (1 + (margen/100)) * tasa_v)
            final_vusd = final_vbs / tasa_v
            final_margen = ((final_vusd / c_usd) - 1) * 100 if c_usd > 0 else margen

            datos = {
                "codigo": cod.upper(), "nombre": nom.upper(),
                "costo_bs": c_bs, "costo_usd": c_usd,
                "margen": round(final_margen, 2),
                "venta_usd": round(final_vusd, 2),
                "venta_bs": round(final_vbs, 2)
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Producto Guardado!")
            st.rerun()

    st.divider()
    st.subheader("📋 Inventario Registrado")
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    if not df.empty:
        st.dataframe(df[["nombre", "costo_usd", "margen", "venta_bs"]], use_container_width=True, hide_index=True)
