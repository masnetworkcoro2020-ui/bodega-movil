import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="BODEGA PRO V2 - GESTIÓN TOTAL", layout="centered")

# 2. CONEXIÓN (TU LLAVE MAESTRA)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

logo_url = "https://raw.githubusercontent.com/masnetworkcoro2020-ui/bodega-movil/main/logo.png"

# 3. ESTILOS CSS (Tus colores originales de inventario.py)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    .main-logo {{ display: flex; justify-content: center; padding: 10px; }}
    /* Colores de tus campos originales */
    input[aria-label="Costo Bs. (Fijo)"] {{ background-color: #fcf3cf !important; }}
    input[aria-label="Costo $"] {{ background-color: #ebedef !important; }}
    input[aria-label="Venta Bs. (Móvil)"] {{ background-color: #d4efdf !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SEGURO ---
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
    # --- INTERFAZ POST-LOGIN ---
    # Obtener Tasa Actual (ID: 1)
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_tasa.data[0]['valor']) if res_tasa.data else 40.0

    pestanas = st.tabs(["💰 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

    with pestanas[0]:
        st.metric("Tasa Actual", f"Bs. {tasa_v:,.2f}")
        nueva_tasa = st.number_input("Cambiar Tasa", value=tasa_v)
        if st.button("💾 ACTUALIZAR TASA"):
            supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
            st.success("Tasa guardada")
            st.rerun()

    with pestanas[1]:
        st.subheader("📦 Gestión de Productos")
        
        # --- LÓGICA DE ESCANEO ---
        # Activamos la cámara del celular para leer código de barras
        codigo_escaneado = st.camera_input("📷 ESCANEAR CÓDIGO DE BARRAS")
        
        # Buscador manual por si la cámara no enfoca bien
        busq = st.text_input("🔍 O busca por nombre...").upper()
        
        res_p = supabase.table("productos").select("*").execute()
        df = pd.DataFrame(res_p.data)
        
        if not df.empty:
            # Seleccionar producto
            opciones = ["-- NUEVO PRODUCTO --"] + sorted(df['nombre'].tolist())
            seleccion = st.selectbox("Producto Seleccionado", opciones)

            # --- FORMULARIO CON TU LÓGICA DE RECALCULO ---
            with st.form("form_inventario"):
                # Si hay selección, traemos los datos
                fila = df[df['nombre'] == seleccion].iloc[0] if seleccion != "-- NUEVO PRODUCTO --" else None
                
                cod = st.text_input("Código", value=str(fila['codigo']) if fila is not None else "")
                nom = st.text_input("Producto", value=str(fila['nombre']) if fila is not None else "")
                
                c_bs = st.number_input("Costo Bs. (Fijo)", value=float(fila['costo_bs']) if fila is not None else 0.0)
                c_usd = st.number_input("Costo $", value=float(fila['costo_usd']) if fila is not None else 0.0)
                margen = st.number_input("Margen %", value=float(fila['margen']) if fila is not None else 25.0)
                
                # Cálculo automático estilo tu función recalcular()
                v_usd = c_usd * (1 + (margen/100))
                v_bs = v_usd * tasa_v
                
                st.write(f"**Venta sugerida: ${v_usd:.2f} / Bs. {v_bs:.2f}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 GUARDAR"):
                        datos = {
                            "codigo": cod.upper(), "nombre": nom.upper(),
                            "costo_bs": c_bs, "costo_usd": c_usd,
                            "margen": margen, "venta_usd": v_usd, "venta_bs": v_bs
                        }
                        if seleccion == "-- NUEVO PRODUCTO --":
                            supabase.table("productos").insert(datos).execute()
                        else:
                            supabase.table("productos").update(datos).eq("nombre", seleccion).execute()
                        st.success("¡Operación exitosa!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("🗑️ ELIMINAR"):
                        if seleccion != "-- NUEVO PRODUCTO --":
                            supabase.table("productos").delete().eq("nombre", seleccion).execute()
                            st.rerun()

    with pestanas[2]:
        st.write("Panel de Usuarios")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
