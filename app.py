import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd
from datetime import datetime

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence ERP", layout="centered")
supabase = conectar()

def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa = obtener_tasa()

# --- ESTADO DE SESIÓN ---
if 'auth' not in st.session_state: st.session_state.auth = None
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""

# --- LOGIN (Usando tus usuarios de Supabase) ---
if not st.session_state.auth:
    st.title("🔐 Acceso")
    u = st.text_input("Usuario:").lower().strip()
    p = st.text_input("Clave:", type="password")
    if st.button("Entrar"):
        # Verifica contra tu tabla real
        res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
        if res.data:
            st.session_state.auth = res.data[0]
            st.rerun()
        else: st.error("Clave incorrecta.")
    st.stop()

# --- INTERFAZ ---
st.sidebar.title(f"👤 {st.session_state.auth['usuario'].upper()}")
st.sidebar.metric("Tasa BCV", f"{tasa} Bs/$")

menu = ["📝 Gestión 360°", "🛒 Ventas", "⚙️ Tasa", "📋 Historial"]
opcion = st.sidebar.radio("Menú", menu)

# --- EL ALGORITMO 360 (TAL CUAL COMO TE GUSTA) ---
if opcion == "📝 Gestión 360°":
    st.subheader("📸 Escáner")
    foto = st.camera_input("Escanear")
    if foto:
        img = Image.open(foto)
        detect = decode(img)
        if detect:
            raw = detect[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = raw[1:] if len(raw) == 13 and raw.startswith('0') else raw

    st.divider()
    cod_g = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    
    if cod_g:
        res = supabase.table("productos").select("*").eq("codigo", cod_g).execute()
        p = res.data[0] if res.data else {}
        
        nombre = st.text_input("Nombre", value=p.get('nombre', ''))
        margen = st.number_input("Margen %", value=float(p.get('margen', 30.0)))
        
        col1, col2 = st.columns(2)
        in_cbs = col1.number_input("Costo Bs", value=0.0)
        in_cusd = col2.number_input("Costo USD", value=0.0)
        in_vbs = col1.number_input("Venta Bs", value=0.0)
        in_vusd = col2.number_input("Venta USD", value=0.0)

        # --- AQUÍ ESTÁ TU ALGORITMO SIN CAMBIOS ---
        m = margen / 100
        c_bs, c_usd, v_bs, v_usd = 0.0, 0.0, 0.0, 0.0

        if in_cbs > 0:
            c_bs = in_cbs; c_usd = c_bs / tasa; v_usd = c_usd * (1 + m); v_bs = v_usd * tasa
        elif in_cusd > 0:
            c_usd = in_cusd; c_bs = c_usd * tasa; v_usd = c_usd * (1 + m); v_bs = v_usd * tasa
        elif in_vbs > 0:
            v_bs = in_vbs; v_usd = v_bs / tasa; c_usd = v_usd / (1 + m); c_bs = c_usd * tasa
        elif in_vusd > 0:
            v_usd = in_vusd; v_bs = v_usd * tasa; c_usd = v_usd / (1 + m); c_bs = c_usd * tasa
        else:
            c_usd = float(p.get('costo_usd', 0.0))
            c_bs = float(p.get('costo_bs', 0.0))
            v_usd = float(p.get('venta_usd', 0.0))
            v_bs = v_usd * tasa

        st.metric("VENTA FINAL", f"{v_bs:.2f} Bs", f"{v_usd:.2f} $")

        if st.button("💾 GUARDAR"):
            datos = {"codigo": cod_g, "nombre": nombre.upper(), "margen": margen, "costo_bs": round(c_bs, 2), "costo_usd": round(c_usd, 2), "venta_bs": round(v_bs, 2), "venta_usd": round(v_usd, 2)}
            if p: supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
            else: supabase.table("productos").insert(datos).execute()
            st.success("Listo.")

# --- MÓDULOS EXTRAS (POR SEPARADO) ---
elif opcion == "🛒 Ventas":
    st.subheader("Registrar Venta")
    # Lógica de venta simple
    pass

elif opcion == "⚙️ Tasa":
    st.subheader("Cambiar Tasa")
    nueva = st.number_input("Tasa:", value=tasa)
    if st.button("Actualizar"):
        supabase.table("ajustes").update({"valor": nueva}).eq("id", 1).execute()
        st.rerun()
