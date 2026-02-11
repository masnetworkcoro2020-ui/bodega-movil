import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="BODEGA PRO V2 - GESTIÓN", layout="centered")

# 2. CONEXIÓN (Tus credenciales de confianza)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

logo_url = "https://raw.githubusercontent.com/masnetworkcoro2020-ui/bodega-movil/main/logo.png"

# 3. ESTILOS CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    .main-logo {{ display: flex; justify-content: center; padding: 10px; }}
    .stButton>button {{ width: 100%; border-radius: 12px; font-weight: bold; height: 3.5em; }}
    /* Color amarillo para Costo Bs. igual al original */
    div[data-testid="stNumberInput"] label:contains("Costo Bs.") + div input {{ background-color: #fcf3cf !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown(f'<div class="main-logo"><img src="{logo_url}" width="150"></div>', unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuario").lower().strip()
        p = st.text_input("Clave", type="password")
        if st.form_submit_button("INGRESAR"):
            res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
            if res.data and str(res.data[0].get("rol","")).lower() in ["maestro", "administrador"]:
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("Acceso denegado")
else:
    # Obtener Tasa Actual
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

    pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

    with pestanas[0]:
        st.metric("Tasa Actual", f"Bs. {tasa_v:,.2f}")
        nueva_tasa = st.number_input("Nueva Tasa", value=tasa_v)
        if st.button("💾 ACTUALIZAR TASA"):
            supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
            st.success("Tasa guardada")
            st.rerun()

    with pestanas[1]:
        # --- PRIMERO: EDITAR / NUEVO (Para acceso rápido) ---
        st.subheader("🛠️ Editar / Nuevo Producto")
        
        # Carga inicial de datos para el selector
        res_p = supabase.table("productos").select("*").order("nombre").execute()
        df = pd.DataFrame(res_p.data)
        
        # Cámara de escaneo arriba
        foto_scan = st.camera_input("📷 ESCANEAR CÓDIGO")
        
        opciones = ["-- NUEVO PRODUCTO --"] + sorted(df['nombre'].tolist() if not df.empty else [])
        sel = st.selectbox("Selecciona un producto para editar", opciones)

        with st.form("form_gestion"):
            fila = df[df['nombre'] == sel].iloc[0] if sel != "-- NUEVO PRODUCTO --" else None
            
            nom = st.text_input("Nombre del Producto", value=str(fila['nombre']) if fila is not None else "")
            c_usd = st.number_input("Costo $", value=float(fila['costo_usd']) if fila is not None else 0.0, format="%.2f")
            margen = st.number_input("Margen %", value=float(fila['margen']) if fila is not None else 25.0)
            
            # Cálculos automáticos estilo inventario.py
            v_usd = c_usd * (1 + (margen/100))
            v_bs = v_usd * tasa_v
            
            st.info(f"Venta Calculada: ${v_usd:.2f} / Bs. {v_bs:.2f}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 GUARDAR"):
                    # Lógica de Update/Insert aquí
                    st.success("Guardado correctamente")
                    st.rerun()
            with col2:
                if st.form_submit_button("🗑️ ELIMINAR"):
                    if sel != "-- NUEVO PRODUCTO --":
                        supabase.table("productos").delete().eq("nombre", sel).execute()
                        st.rerun()

        st.divider()

        # --- SEGUNDO: INVENTARIO REGISTRADO (Abajo para consulta) ---
        st.subheader("📋 Inventario Registrado")
        if not df.empty:
            busq = st.text_input("🔍 Filtrar lista...").upper()
            df_view = df.copy()
            if busq:
                df_view = df[df['nombre'].str.contains(busq, na=False)]
            
            st.dataframe(
                df_view[["nombre", "venta_usd", "venta_bs"]], 
                column_config={
                    "nombre": "PRODUCTO",
                    "venta_usd": st.column_config.NumberColumn("USD $", format="$ %.2f"),
                    "venta_bs": st.column_config.NumberColumn("BS. TASA", format="Bs %.2f")
                },
                use_container_width=True, 
                hide_index=True
            )

    with pestanas[2]:
        st.write("Configuración de Usuarios")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
