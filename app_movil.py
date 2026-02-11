import streamlit as st
from supabase import create_client
import pandas as pd

# CONFIGURACIÓN DE PÁGINA (ESTILO BODEGA PRO)
st.set_page_config(page_title="BODEGA PRO V2 - MÓVIL", layout="centered")

# CONEXIÓN DIRECTA (USANDO TUS DATOS DE CONFIG.PY)
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# --- ESTILO DE COLORES ORIGINALES ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .tasa-btn { background-color: #FFD700; color: black; } /* Amarillo */
    .inv-btn { background-color: #1f538d; color: white; }  /* Azul */
    .user-btn { background-color: #ff8c00; color: white; } /* Naranja */
    </style>
    """, unsafe_allow_name=True)

# --- MENÚ PRINCIPAL ---
st.title("🏪 BODEGA PRO MÓVIL")
menu = st.tabs(["📊 TASA", "📦 INVENTARIO", "👥 USUARIOS"])

# --- 1. PESTAÑA TASA (AMARILLO) ---
with menu[0]:
    st.subheader("Actualizar Tasa BCV")
    # Buscamos la tasa actual en tu tabla 'ajustes' ID: 1
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_actual = res_tasa.data[0]['valor'] if res_tasa.data else 0.0
    
    st.metric("Tasa Actual en Sistema", f"Bs. {tasa_actual}")
    nueva_tasa = st.number_input("Nueva Tasa de Venta", value=float(tasa_actual), step=0.01)
    
    if st.button("💾 GUARDAR NUEVA TASA"):
        supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
        st.success(f"¡Tasa actualizada a Bs. {nueva_tasa}!")
        st.rerun()

# --- 2. PESTAÑA INVENTARIO (AZUL) ---
with menu[1]:
    st.subheader("Gestión de Productos")
    modo_inv = st.radio("Acción:", ["Ver/Buscar", "Agregar Nuevo"], horizontal=True)
    
    if modo_inv == "Ver/Buscar":
        busqueda = st.text_input("🔍 Nombre del producto...")
        res_inv = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
        df = pd.DataFrame(res_inv.data)
        if not df.empty and busqueda:
            df = df[df['nombre'].str.contains(busqueda, case=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    else:
        with st.form("add_prod"):
            nombre_p = st.text_input("Nombre del Producto")
            p_usd = st.number_input("Precio USD", min_value=0.0, step=0.1)
            # Cálculo automático en base a la tasa
            p_bs = p_usd * float(tasa_actual)
            st.info(f"Precio calculado: Bs. {p_bs:,.2f}")
            
            if st.form_submit_button("➕ REGISTRAR EN INVENTARIO"):
                if nombre_p:
                    supabase.table("productos").insert({
                        "nombre": nombre_p.upper(), 
                        "venta_usd": p_usd, 
                        "venta_bs": p_bs
                    }).execute()
                    st.success("¡Producto agregado con éxito!")
                else:
                    st.error("Falta el nombre")

# --- 3. PESTAÑA USUARIOS (NARANJA) ---
with menu[2]:
    st.subheader("Control de Acceso")
    with st.form("add_user"):
        new_u = st.text_input("Usuario (Login)")
        new_p = st.text_input("Clave", type="password")
        new_r = st.selectbox("Rol", ["Administrador", "Operador"])
        
        if st.form_submit_button("👤 CREAR USUARIO"):
            if new_u and new_p:
                supabase.table("usuarios").insert({
                    "usuario": new_u.lower(), 
                    "clave": new_p, 
                    "rol": new_r
                }).execute()
                st.success(f"Usuario {new_u} creado")
            else:
                st.warning("Completa los campos")
