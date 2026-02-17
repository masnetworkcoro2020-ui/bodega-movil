import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd
from datetime import datetime

# 1. Configuración
st.set_page_config(page_title="Royal Essence Pro", layout="centered")
supabase = conectar()

def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

def verificar_acceso(user_input, pass_input):
    try:
        # Verifica contra tu tabla real de usuarios
        res = supabase.table("usuarios").select("*").eq("usuario", user_input).eq("clave", pass_input).execute()
        return res.data[0] if res.data else None
    except: return None

tasa = obtener_tasa()

# --- SESIÓN ---
if 'auth' not in st.session_state: st.session_state.auth = None
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""

# --- LOGIN ---
if not st.session_state.auth:
    st.title("🔐 Acceso Royal Essence")
    u = st.text_input("Usuario:").lower().strip()
    p = st.text_input("Clave:", type="password")
    if st.button("Entrar"):
        user = verificar_acceso(u, p)
        if user:
            st.session_state.auth = user
            st.rerun()
        else: st.error("Usuario o clave incorrecta.")
    st.stop()

# --- MENÚ ---
st.sidebar.title(f"👤 {st.session_state.auth['usuario'].upper()}")
st.sidebar.metric("Tasa BCV", f"{tasa} Bs/$")

menu = ["📸 Escáner", "🛒 Vender", "📝 Gestión 360°", "📋 Historial", "⚙️ Ajustes"]
opcion = st.sidebar.radio("Menú", menu)

# --- LÓGICA DE VENTAS ---
if opcion == "🛒 Vender":
    st.subheader("Punto de Venta")
    cod = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    if cod:
        res = supabase.table("productos").select("*").eq("codigo", cod).execute()
        if res.data:
            p = res.data[0]
            st.write(f"### {p['nombre']}")
            st.metric("Precio Bs", f"{p['venta_bs']:.2f} Bs", f"{p['venta_usd']} $")
            
            cant = st.number_input("Cantidad", min_value=1, value=1)
            if st.button("🔥 REGISTRAR VENTA"):
                # Solo historial, quitamos 'existencia' para evitar errores
                supabase.table("ventas").insert({
                    "producto": p['nombre'], 
                    "cantidad": cant, 
                    "total_usd": float(p['venta_usd']) * cant,
                    "vendedor": st.session_state.auth['usuario']
                }).execute()
                st.success("✅ Venta registrada")
                st.session_state.codigo_escaneado = ""
        else: st.error("No existe ese producto.")

# --- LÓGICA GESTIÓN 360° (CORREGIDA) ---
elif opcion == "📝 Gestión 360°":
    st.subheader("Algoritmo de Precios 360°")
    cod_g = st.text_input("Escanear/Escribir Código:", value=st.session_state.codigo_escaneado)
    
    if cod_g:
        # Buscamos el producto primero
        res = supabase.table("productos").select("*").eq("codigo", cod_g).execute()
        prod_db = res.data[0] if res.data else None
        
        if prod_db: st.warning(f"Editando: {prod_db['nombre']}")
        else: st.info("✨ Producto Nuevo")

        with st.form("form_360_final"):
            nombre = st.text_input("Nombre", value=prod_db['nombre'] if prod_db else "")
            margen = st.number_input("Margen %", value=float(prod_db['margen'] if prod_db else 30.0))
            
            col1, col2 = st.columns(2)
            c_bs_in = col1.number_input("Costo Bs", value=0.0)
            c_usd_in = col2.number_input("Costo USD", value=0.0)
            v_bs_in = col1.number_input("Venta Bs", value=0.0)
            v_usd_in = col2.number_input("Venta USD", value=0.0)
            
            # El botón de formulario
            aplicar = st.form_submit_button("💾 GUARDAR CAMBIOS")
            
            if aplicar:
                m = margen / 100
                # Lógica 360°
                if c_bs_in > 0: 
                    c_bs, c_usd = c_bs_in, c_bs_in/tasa
                    v_usd = c_usd*(1+m); v_bs = v_usd*tasa
                elif c_usd_in > 0: 
                    c_usd, c_bs = c_usd_in, c_usd_in*tasa
                    v_usd = c_usd*(1+m); v_bs = v_usd*tasa
                elif v_bs_in > 0: 
                    v_bs, v_usd = v_bs_in, v_bs_in/tasa
                    c_usd = v_usd/(1+m); c_bs = c_usd*tasa
                elif v_usd_in > 0: 
                    v_usd, v_bs = v_usd_in, v_usd_in*tasa
                    c_usd = v_usd/(1+m); c_bs = c_usd*tasa
                else:
                    st.error("Mete un precio mano")
                    st.stop()

                datos = {
                    "codigo": cod_g, "nombre": nombre.upper(), "margen": margen,
                    "costo_bs": round(c_bs, 2), "costo_usd": round(c_usd, 2),
                    "venta_bs": round(v_bs, 2), "venta_usd": round(v_usd, 2)
                }

                if prod_db:
                    # Usamos el identifi de tu tabla
                    supabase.table("productos").update(datos).eq("identifi", prod_db['identifi']).execute()
                else:
                    supabase.table("productos").insert(datos).execute()
                
                st.success("✅ Guardado en la nube")
                st.session_state.codigo_escaneado = ""

# --- AJUSTES TASA ---
elif opcion == "⚙️ Ajustes":
    st.subheader("Tasa del Sistema")
    nueva = st.number_input("Nueva Tasa:", value=tasa)
    if st.button("Actualizar"):
        supabase.table("ajustes").update({"valor": nueva}).eq("id", 1).execute()
        st.success("Tasa actualizada")
        st.rerun()

# --- ESCÁNER ---
elif opcion == "📸 Escáner":
    foto = st.camera_input("Escanear")
    if foto:
        img = Image.open(foto)
        d = decode(img)
        if d:
            st.session_state.codigo_escaneado = d[0].data.decode('utf-8')
            st.success(f"Código: {st.session_state.codigo_escaneado}")
