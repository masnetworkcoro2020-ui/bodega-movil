import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd
from datetime import datetime

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Pro", layout="centered")
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

# --- LOGIN (CLAVE DE ACCESO) ---
if not st.session_state.auth:
    st.title("🔐 Acceso al Sistema")
    u = st.text_input("Usuario:").lower().strip()
    p = st.text_input("Clave:", type="password")
    if st.button("Iniciar Sesión"):
        res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", p).execute()
        if res.data:
            st.session_state.auth = res.data[0]
            st.rerun()
        else: st.error("Clave o usuario incorrecto.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title(f"👤 {st.session_state.auth['usuario'].upper()}")
st.sidebar.metric("Tasa BCV Actual", f"{tasa} Bs/$")

menu = ["📸 Escáner / Gestión 360°", "🛒 Ventas / Facturación", "⚙️ Ajustes de Tasa", "📋 Historial"]
opcion = st.sidebar.radio("Menú Principal", menu)

# --- MODULO 1: ESCÁNER Y GESTIÓN 360° (TODO JUNTO COMO QUERÍAS) ---
if opcion == "📸 Escáner / Gestión 360°":
    st.subheader("📸 Escáner de Barras")
    foto = st.camera_input("Enfoca el código")
    if foto:
        img = Image.open(foto)
        detect = decode(img)
        if detect:
            lectura = detect[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"Código capturado: {st.session_state.codigo_escaneado}")

    st.divider()
    
    st.subheader("📝 Algoritmo de Precios 360°")
    cod_g = st.text_input("Código de Producto:", value=st.session_state.codigo_escaneado)
    
    if cod_g:
        res = supabase.table("productos").select("*").eq("codigo", cod_g).execute()
        prod = res.data[0] if res.data else {}
        
        nombre = st.text_input("Nombre del Producto", value=prod.get('nombre', ''))
        margen = st.number_input("Margen %", value=float(prod.get('margen', 30.0)))
        
        st.info("Ingresa UN precio y los demás se calcularán solos:")
        c1, c2 = st.columns(2)
        in_cbs = c1.number_input("Costo Bs", value=0.0)
        in_cusd = c2.number_input("Costo USD", value=0.0)
        in_vbs = c1.number_input("Venta Bs", value=0.0)
        in_vusd = c2.number_input("Venta USD", value=0.0)

        # --- LÓGICA MATEMÁTICA 360° (IDÉNTICA A TU INVENTARIO.PY) ---
        m = margen / 100
        c_bs, c_usd, v_bs, v_usd = 0.0, 0.0, 0.0, 0.0

        if in_cbs > 0: c_bs=in_cbs; c_usd=c_bs/tasa; v_usd=c_usd*(1+m); v_bs=v_usd*tasa
        elif in_cusd > 0: c_usd=in_cusd; c_bs=c_usd*tasa; v_usd=c_usd*(1+m); v_bs=v_usd*tasa
        elif in_vbs > 0: v_bs=in_vbs; v_usd=v_bs/tasa; c_usd=v_usd/(1+m); c_bs=c_usd*tasa
        elif in_vusd > 0: v_usd=in_vusd; v_bs=v_usd*tasa; c_usd=v_usd/(1+m); c_bs=c_usd*tasa
        else:
            c_usd = float(prod.get('costo_usd', 0.0)); c_bs = float(prod.get('costo_bs', 0.0))
            v_usd = float(prod.get('venta_usd', 0.0)); v_bs = v_usd * tasa

        st.markdown("### 📊 Previsión de Precios")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("VENTA BS", f"{v_bs:.2f}")
        res_col2.metric("VENTA USD", f"{v_usd:.2f} $")

        if st.button("💾 GUARDAR CAMBIOS EN LA NUBE"):
            datos = {
                "codigo": cod_g, "nombre": nombre.upper(), "margen": margen,
                "costo_bs": round(c_bs, 2), "costo_usd": round(c_usd, 2),
                "venta_bs": round(v_bs, 2), "venta_usd": round(v_usd, 2)
            }
            if prod:
                supabase.table("productos").update(datos).eq("identifi", prod['identifi']).execute()
            else:
                supabase.table("productos").insert(datos).execute()
            st.success("¡Sincronizado con éxito!")

# --- MODULO 2: VENTAS / FACTURACIÓN ---
elif opcion == "🛒 Ventas / Facturación":
    st.subheader("🛒 Punto de Venta Móvil")
    cod_v = st.text_input("Escanear o escribir código:", value=st.session_state.codigo_escaneado)
    if cod_v:
        res = supabase.table("productos").select("*").eq("codigo", cod_v).execute()
        if res.data:
            p = res.data[0]
            st.write(f"### {p['nombre']}")
            # Precio actualizado a la tasa actual
            v_bs_fresca = float(p['venta_usd']) * tasa
            st.metric("A cobrar en Bs", f"{v_bs_fresca:.2f} Bs", f"{p['venta_usd']} $")
            
            cant = st.number_input("Cantidad:", min_value=1, value=1)
            if st.button("✅ REGISTRAR FACTURA"):
                supabase.table("ventas").insert({
                    "producto": p['nombre'], "cantidad": cant, 
                    "total_usd": float(p['venta_usd']) * cant,
                    "vendedor": st.session_state.auth['usuario'],
                    "fecha": datetime.now().isoformat()
                }).execute()
                st.success("Venta guardada.")
                st.session_state.codigo_escaneado = ""
        else: st.error("Producto no registrado.")

# --- MODULO 3: TASA BCV ---
elif opcion == "⚙️ Ajustes de Tasa":
    st.subheader("⚙️ Configuración de Tasa")
    nueva_tasa = st.number_input("Nueva Tasa del Día:", value=tasa, format="%.2f")
    if st.button("Actualizar en todo el Sistema"):
        supabase.table("ajustes").update({"valor": nueva_tasa}).eq("id", 1).execute()
        st.success(f"Tasa cambiada a {nueva_tasa}. La PC también se actualizó.")
        st.rerun()

# --- MODULO 4: HISTORIAL ---
elif opcion == "📋 Historial":
    st.subheader("📋 Ventas del Día")
    res = supabase.table("ventas").select("*").order("id", desc=True).limit(20).execute()
    if res.data: st.dataframe(pd.DataFrame(res.data)[['fecha', 'producto', 'cantidad', 'total_usd', 'vendedor']])
