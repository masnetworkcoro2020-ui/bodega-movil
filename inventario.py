import streamlit as st
import pandas as pd

def mostrar(supabase):
    # 1. Obtener Tasa (ID:1)
    tasa = 1.0
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        tasa = float(res.data[0]['valor']) if res.data else 40.0
    except: tasa = 40.0

    # Inicializar estado
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':25.0, 'vusd':0.0, 'vbs':0.0, 'nom':"", 'cod_leido': ""})

    # Lógica de Recálculo 360°
    def recalcular(origen):
        t = tasa
        m = st.session_state.mar / 100
        if origen == "cbs":
            st.session_state.cusd = st.session_state.cbs / t
            st.session_state.vusd = st.session_state.cusd * (1 + m)
            st.session_state.vbs = st.session_state.vusd * t
        elif origen == "cusd":
            st.session_state.cbs = st.session_state.cusd * t
            st.session_state.vusd = st.session_state.cusd * (1 + m)
            st.session_state.vbs = st.session_state.vusd * t
        elif origen == "mar":
            st.session_state.vusd = st.session_state.cusd * (1 + m)
            st.session_state.vbs = st.session_state.vusd * t
        elif origen == "vbs":
            st.session_state.vusd = st.session_state.vbs / t
            st.session_state.cusd = st.session_state.vusd / (1 + m)
            st.session_state.cbs = st.session_state.cusd * t

    # --- ESCÁNER AUTOMÁTICO ---
    # Usamos st.camera_input para capturar. Al procesar la imagen detectamos el código.
    with st.expander("📷 ABRIR ESCÁNER (AUTO-LECTURA)", expanded=False):
        foto = st.camera_input("Enfoca el código de barras")
        if foto:
            # Nota: Streamlit procesa la imagen. Para que sea "automático" 
            # el usuario solo tiene que apuntar y darle al botón de capturar.
            import cv2
            import numpy as np
            from pyzbar import pyzbar
            
            file_bytes = np.asarray(bytearray(foto.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            codigos = pyzbar.decode(img)
            
            for objeto in codigos:
                st.session_state.cod_leido = objeto.data.decode('utf-8')
                st.toast(f"✅ Código detectado: {st.session_state.cod_leido}")

    # --- CAMPO CÓDIGO (Se llena solo si la cámara leyó algo) ---
    cod = st.text_input("Código:", value=st.session_state.cod_leido, key="ent_cod").strip()

    if cod:
        if st.session_state.get('last_cod') != cod:
            res_p = supabase.table("productos").select("*").eq("codigo", cod).execute()
            if res_p.data:
                p = res_p.data[0]
                st.session_state.update({
                    'nom': p['nombre'], 'cbs': float(p['costo_bs']),
                    'cusd': float(p['costo_usd']), 'mar': float(p['margen']),
                    'last_cod': cod
                })
                recalcular("cusd")

    # Campos de entrada con tus Binds
    st.text_input("Nombre:", key="nom")
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Costo Bs:", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
        st.number_input("Margen %:", key="mar", on_change=recalcular, args=("mar",), step=1.0)
        st.number_input("Venta $:", key="vusd", format="%.2f", disabled=True)
    
    with col2:
        st.number_input("Costo $:", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
        st.number_input("Venta Bs:", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

    # Botones
    st.write("")
    if st.button("💾 GUARDAR / ACTUALIZAR", use_container_width=True, type="primary"):
        data = {
            "codigo": cod, "nombre": st.session_state.nom,
            "costo_bs": st.session_state.cbs, "costo_usd": st.session_state.cusd,
            "margen": st.session_state.mar, "venta_usd": st.session_state.vusd,
            "venta_bs": st.session_state.vbs
        }
        supabase.table("productos").upsert(data).execute()
        st.success("Guardado en Bodega.")

    # Tabla
    st.divider()
    res_all = supabase.table("productos").select("*").order("nombre").execute()
    if res_all.data:
        df = pd.DataFrame(res_all.data)
        st.dataframe(df[["codigo", "nombre", "costo_bs", "costo_usd", "margen", "venta_usd", "venta_bs"]], use_container_width=True)
