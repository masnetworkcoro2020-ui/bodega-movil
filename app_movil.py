import streamlit as st
from supabase import create_client
import pandas as pd

# CONFIGURACIÓN ESTILO BODEGA PRO V2
st.set_page_config(page_title="BODEGA PRO V2 - MÓVIL", layout="centered")

# CONEXIÓN USANDO TUS CREDENCIALES ORIGINALES
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"
supabase = create_client(URL, KEY)

# --- MENÚ DE NAVEGACIÓN TIPO APP ---
st.title("📱 PANEL DE CONTROL MÓVIL")
tab_tasa, tab_inv, tab_user = st.tabs(["💰 TASA BCV", "📦 INVENTARIO", "👥 USUARIOS"])

# --- 1. GESTIÓN DE TASA (IGUAL A TU INVENTARIO.PY) ---
with tab_tasa:
    st.subheader("Control de Tasa de Cambio")
    # Consulta la tasa usando tu ID:1 original
    res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_actual = float(res_tasa.data[0]['valor']) if res_tasa.data else 0.0
    
    st.metric(label="Tasa Actual en Sistema", value=f"Bs. {tasa_actual:,.2f}")
    nueva_tasa = st.number_input("Cambiar Tasa (Bs.)", value=tasa_actual, step=0.01)
    
    if st.button("✅ ACTUALIZAR TASA EN TODO EL SISTEMA"):
        supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("id", 1).execute()
        st.success(f"¡Tasa actualizada! Tu computadora ahora también verá: {nueva_tasa}")
        st.rerun()

# --- 2. GESTIÓN DE INVENTARIO (IGUAL A TU INVENTARIO.PY) ---
with tab_inv:
    st.subheader("Inventario de Productos")
    opc = st.radio("Acción", ["Ver/Buscar", "Nuevo Producto"], horizontal=True)
    
    if opc == "Ver/Buscar":
        busqueda = st.text_input("🔍 Buscar por nombre...")
        res_prod = supabase.table("productos").select("nombre, venta_usd, venta_bs").execute()
        df = pd.DataFrame(res_prod.data)
        if not df.empty and busqueda:
            df = df[df['nombre'].str.contains(busqueda.upper(), case=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    else:
        with st.form("form_inv"):
            nom = st.text_input("Nombre del Producto")
            p_usd = st.number_input("Precio en $", min_value=0.0, step=0.01)
            # Calcula el precio en Bs automáticamente como lo hace tu programa
            p_bs = p_usd * tasa_actual
            st.write(f"Precio en Bolívares: **Bs. {p_bs:,.2f}**")
            
            if st.form_submit_button("💾 GUARDAR"):
                if nom:
                    supabase.table("productos").insert({
                        "nombre": nom.upper(),
                        "venta_usd": p_usd,
                        "venta_bs": p_bs
                    }).execute()
                    st.success("Producto guardado correctamente")
                else:
                    st.error("Escribe un nombre")

# --- 3. GESTIÓN DE USUARIOS (IGUAL A TU USUARIOS.PY) ---
with tab_user:
    st.subheader("Usuarios del Sistema")
    with st.form("form_user"):
        u_nom = st.text_input("Nombre de Usuario")
        u_pass = st.text_input("Contraseña", type="password")
        u_rol = st.selectbox("Rol", ["Administrador", "Operador"])
        
        if st.form_submit_button("👤 CREAR USUARIO"):
            if u_nom and u_pass:
                supabase.table("usuarios").insert({
                    "usuario": u_nom.lower().strip(),
                    "clave": u_pass,
                    "rol": u_rol
                }).execute()
                st.success(f"Usuario '{u_nom}' creado")
