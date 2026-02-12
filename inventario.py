import streamlit as st
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image

def mostrar(supabase):
    st.markdown("### 📦 INVENTARIO 360° (MÓVIL)")

    # --- TU LÓGICA DE TASA (ID:1) ---
    tasa = 40.0
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res.data: tasa = float(res.data[0]['valor'])
    except: pass

    # --- ESTADO DE LOS CAMPOS (Variables espejo) ---
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':25.0, 'vbs':0.0, 'nom':"", 'last_cod': ""})

    # --- TU FÓRMULA 360° ORIGINAL (Sin cambios) ---
    def recalcular(origen):
        t = tasa
        m = st.session_state.mar / 100
        if origen == "cbs":
            st.session_state.cusd = st.session_state.cbs / t
            st.session_state.vbs = (st.session_state.cusd * (1 + m)) * t
        elif origen == "cusd":
            st.session_state.cbs = st.session_state.cusd * t
            st.session_state.vbs = (st.session_state.cusd * (1 + m)) * t
        elif origen == "vbs":
            vusd_temp = st.session_state.vbs / t
            st.session_state.cusd = vusd_temp / (1 + m)
            st.session_state.cbs = st.session_state.cusd * t
        elif origen == "mar":
            st.session_state.vbs = (st.session_state.cusd * (1 + m)) * t

    # --- ESCÁNER CON CÁMARA DEL TELÉFONO ---
    st.write("📷 **ESCANEAR CÓDIGO**")
    img_file = st.camera_input("Enfoque el código de barras")

    if img_file:
        # Convertir foto del cel a formato que pyzbar entienda
        img = Image.open(img_file)
        img_np = np.array(img)
        codigos = pyzbar.decode(img_np)
        
        for c in codigos:
            codigo_detectado = c.data.decode('utf-8')
            if codigo_detectado != st.session_state.last_cod:
                st.session_state.last_cod = codigo_detectado
                # Búsqueda en DB (Tu lógica cargar_datos_guardados)
                try:
                    p = supabase.table("productos").select("*").eq("codigo", codigo_detectado).execute()
                    if p.data:
                        prod = p.data[0]
                        st.session_state.update({
                            'nom': prod['nombre'], 'cbs': float(prod['costo_bs']),
                            'cusd': float(prod['costo_usd']), 'mar': float(prod['margen'])
                        })
                        recalcular("cusd")
                        st.success(f"Código detectado: {codigo_detectado}")
                except: pass

    # --- CAMPOS DE LLENADO (Fórmula 360°) ---
    cod_manual = st.text_input("CÓDIGO MANUAL", value=st.session_state.last_cod)
    st.text_input("NOMBRE DEL PRODUCTO", key="nom")

    c1, c2 = st.columns(2)
    with c1:
        st.number_input("COSTO BS", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
        st.number_input("MARGEN %", key="mar", on_change=recalcular, args=("mar",), step=1.0)
    with c2:
        st.number_input("COSTO $", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
        st.number_input("VENTA BS", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

    # Cuadro de precio final (Tu diseño verde)
    st.success(f"### PRECIO VENTA: Bs. {st.session_state.vbs:,.2f}")

    if st.button("💾 GUARDAR EN INVENTARIO", use_container_width=True):
        try:
            supabase.table("productos").upsert({
                "codigo": st.session_state.last_cod if st.session_state.last_cod else cod_manual,
                "nombre": st.session_state.nom, "costo_bs": st.session_state.cbs,
                "costo_usd": st.session_state.cusd, "margen": st.session_state.mar,
                "venta_bs": st.session_state.vbs
            }).execute()
            st.balloons()
        except Exception as e: st.error(f"Error: {e}")
