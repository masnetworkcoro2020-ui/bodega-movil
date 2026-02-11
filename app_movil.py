import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="BODEGA PRO V2 - GESTIÓN", layout="centered")

# 2. CONEXIÓN (Mantenemos tus credenciales)
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
    .btn-update {{ background-color: #1f538d; color: white; }}
    .btn-delete {{ background-color: #d32f2f; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN (Tu usuario 'jmaar' con rol 'maestro' ya entra aquí) ---
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
    st.markdown(f'<div class="main-logo"><img src="{logo_url}" width="100"></div>', unsafe_allow_html=True)
    
    # 4. LÓGICA DE TASA
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
        # --- BUSCADOR Y TABLA ---
        busq = st.text_input("🔍 Buscar para editar...").upper()
        res_p = supabase.table("productos").select("*").execute()
        df = pd.DataFrame(res_p.data)
        
        if not df.empty:
            if busq:
                df = df[df['nombre'].str.contains(busq, na=False)]
            st.dataframe(df[["nombre", "venta_usd", "venta_bs"]], use_container_width=True, hide_index=True)

            st.divider()
            
            # --- FORMULARIO DE GESTIÓN ---
            st.subheader("🛠️ Editar / Agregar")
            # Seleccionar producto de la lista para editar
            opciones = ["-- NUEVO PRODUCTO --"] + sorted(df['nombre'].tolist())
            seleccion = st.selectbox("Selecciona un producto", opciones)

            with st.form("gestion_inv"):
                nombre_p = st.text_input("Nombre del Producto", value="" if seleccion == "-- NUEVO PRODUCTO --" else seleccion)
                precio_u = st.number_input("Precio USD", format="%.2f", value=0.0 if seleccion == "-- NUEVO PRODUCTO --" else float(df[df['nombre']==seleccion]['venta_usd'].values[0]))
                
                col1, col2 = st.columns(2)
                with col1:
                    save_btn = st.form_submit_button("💾 GUARDAR/SUBIR")
                with col2:
                    del_btn = st.form_submit_button("🗑️ ELIMINAR")

                if save_btn:
                    p_bs = precio_u * tasa_v
                    if seleccion == "-- NUEVO PRODUCTO --":
                        supabase.table("productos").insert({"nombre": nombre_p.upper(), "venta_usd": precio_u, "venta_bs": p_bs}).execute()
                        st.success("Añadido")
                    else:
                        supabase.table("productos").update({"nombre": nombre_p.upper(), "venta_usd": precio_u, "venta_bs": p_bs}).eq("nombre", seleccion).execute()
                        st.success("Actualizado")
                    st.rerun()

                if del_btn and seleccion != "-- NUEVO PRODUCTO --":
                    supabase.table("productos").delete().eq("nombre", seleccion).execute()
                    st.warning(f"Eliminado: {seleccion}")
                    st.rerun()

    with pestanas[2]:
        st.write("Panel de Usuarios Activo")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state["autenticado"] = False
            st.rerun()
