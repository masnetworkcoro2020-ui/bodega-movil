import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONEXIÓN (Mantenemos tus credenciales)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# 2. ESTILOS CSS (Colores de tus campos originales)
st.markdown("""
    <style>
    /* Amarillo claro para Costo Bs */
    div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; color: black !important; }
    /* Gris para Costo USD */
    div[data-testid="stNumberInput"]:has(label:contains("Costo $")) input { background-color: #ebedef !important; color: black !important; }
    /* Verde para Venta Bs (Móvil) */
    div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; color: black !important; font-weight: bold !important; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENER TASA ACTUAL ---
res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

# --- PESTAÑAS ---
pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

with pestanas[1]:
    st.subheader("🛠️ Gestión de Inventario")
    
    # 1. CARGA DE DATOS
    res_p = supabase.table("productos").select("*").order("nombre").execute()
    df = pd.DataFrame(res_p.data)
    
    # 2. ESCÁNER Y SELECCIÓN
    st.camera_input("📷 ESCANEAR CÓDIGO")
    opciones = ["-- NUEVO PRODUCTO --"] + sorted(df['nombre'].tolist() if not df.empty else [])
    sel = st.selectbox("Selecciona un producto para editar", opciones)
    
    with st.form("form_completo"):
        fila = df[df['nombre'] == sel].iloc[0] if sel != "-- NUEVO PRODUCTO --" else None
        
        # --- CAMPOS CON TU LÓGICA DE INVENTARIO.PY ---
        cod = st.text_input("Código", value=str(fila['codigo']) if fila is not None else "")
        nom = st.text_input("Producto", value=str(fila['nombre']) if fila is not None else "")
        
        col_costos = st.columns(2)
        with col_costos[0]:
            c_bs = st.number_input("Costo Bs. (Fijo)", value=float(fila['costo_bs']) if fila is not None else 0.0, format="%.2f")
        with col_costos[1]:
            c_usd = st.number_input("Costo $", value=float(fila['costo_usd']) if fila is not None else 0.0, format="%.2f")
            
        margen = st.number_input("Margen %", value=float(fila['margen']) if fila is not None else 25.0, step=1.0)
        
        # --- CÁLCULOS MATEMÁTICOS (Tu función recalcular()) ---
        v_usd = c_usd * (1 + (margen/100))
        v_bs = v_usd * tasa_v
        
        # Campo informativo de venta (Verde)
        st.number_input("Venta Bs. (Móvil)", value=v_bs, disabled=True, format="%.2f")
        st.write(f"📊 **Venta Sugerida:** ${v_usd:.2f} USD")

        if st.form_submit_button("💾 GUARDAR / ACTUALIZAR"):
            datos = {
                "codigo": cod.upper(), "nombre": nom.upper(),
                "costo_bs": c_bs, "costo_usd": c_usd,
                "margen": margen, "venta_usd": v_usd, "venta_bs": v_bs
            }
            if sel == "-- NUEVO PRODUCTO --":
                supabase.table("productos").insert(datos).execute()
            else:
                supabase.table("productos").update(datos).eq("nombre", sel).execute()
            st.success("¡Producto sincronizado!")
            st.rerun()

    st.divider()
    # 3. TABLA DE REGISTROS (Abajo como pediste)
    st.subheader("📋 Inventario Registrado")
    if not df.empty:
        st.dataframe(
            df[["nombre", "costo_usd", "venta_usd", "venta_bs"]], 
            column_config={
                "nombre": "PRODUCTO",
                "costo_usd": "COSTO $",
                "venta_usd": "VENTA $",
                "venta_bs": "VENTA BS"
            },
            use_container_width=True, hide_index=True
        )
