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

tasa = obtener_tasa()

# --- SESIÓN ---
if 'auth' not in st.session_state: st.session_state.auth = None
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""

# --- LOGIN (Simplificado para el ejemplo, usa tu lógica de usuarios) ---
if not st.session_state.auth:
    st.title("🔐 Acceso")
    u = st.text_input("Usuario:").lower().strip()
    p = st.text_input("Clave:", type="password")
    if st.button("Entrar"):
        res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
        if res.data:
            st.session_state.auth = res.data[0]
            st.rerun()
    st.stop()

# --- INTERFAZ ---
st.sidebar.metric("Tasa BCV", f"{tasa} Bs/$")
opcion = st.sidebar.radio("Menú", ["📸 Escáner", "🛒 Vender", "📝 Gestión 360°", "⚙️ Ajustes"])

# --- ALGORITMO 360° CON CÁLCULO INSTANTÁNEO ---
if opcion == "📝 Gestión 360°":
    st.subheader("Cerebro de Precios 360°")
    cod_g = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    
    if cod_g:
        res = supabase.table("productos").select("*").eq("codigo", cod_g).execute()
        p = res.data[0] if res.data else {}
        
        # 1. Entradas base (Fuera del form para que recalculen en vivo)
        nombre = st.text_input("Nombre del Producto", value=p.get('nombre', ''))
        margen = st.number_input("Margen de Ganancia %", value=float(p.get('margen', 30.0)))
        
        st.markdown("---")
        st.info("Escribe en UN solo campo para calcular los demás:")
        
        col1, col2 = st.columns(2)
        # Campos de entrada
        in_cbs = col1.number_input("Costo en Bolívares", value=0.0, step=1.0)
        in_cusd = col2.number_input("Costo en Dólares", value=0.0, step=0.1)
        in_vbs = col1.number_input("Venta Final Bs", value=0.0, step=1.0)
        in_vusd = col2.number_input("Venta Final USD", value=0.0, step=0.1)

        # 2. LA LÓGICA MATEMÁTICA (Idéntica a tu inventario.py)
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
            # Si no hay entrada nueva, mostrar lo que ya tiene el producto en DB
            c_usd = float(p.get('costo_usd', 0.0))
            c_bs = float(p.get('costo_bs', 0.0))
            v_usd = float(p.get('venta_usd', 0.0))
            v_bs = v_usd * tasa

        # 3. CUADRO DE RESULTADOS (Visualización antes de guardar)
        with st.container(border=True):
            st.write("### 📊 Previsión 360°")
            r1, r2 = st.columns(2)
            r1.metric("COSTO FINAL", f"{c_bs:.2f} Bs", f"{c_usd:.2f} $")
            r2.metric("VENTA FINAL", f"{v_bs:.2f} Bs", f"{v_usd:.2f} $")
            st.write(f"**Ganancia neta:** {(v_usd - c_usd):.2f} $ por unidad.")

        # 4. BOTÓN DE GUARDADO FINAL
        if st.button("💾 GUARDAR TODO EN LA NUBE"):
            datos = {
                "codigo": cod_g, "nombre": nombre.upper(), "margen": margen,
                "costo_bs": round(c_bs, 2), "costo_usd": round(c_usd, 2),
                "venta_bs": round(v_bs, 2), "venta_usd": round(v_usd, 2)
            }
            if p:
                supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
            else:
                supabase.table("productos").insert(datos).execute()
            st.success("✅ ¡Sincronizado!")
