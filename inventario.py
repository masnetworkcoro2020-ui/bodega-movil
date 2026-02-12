import streamlit as st
import pandas as pd

def mostrar(supabase):
    st.title("📦 Inventario 360°")

    # 1. Obtener Tasa con Seguro
    tasa = 40.0
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res_tasa.data:
            tasa = float(res_tasa.data[0]['valor'])
    except:
        st.warning("Conexión lenta con la base de datos...")

    # Estado de la calculadora
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':30.0, 'vusd':0.0, 'vbs':0.0, 'nom':""})

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
        elif origen == "vbs":
            st.session_state.vusd = st.session_state.vbs / t
            st.session_state.cusd = st.session_state.vusd / (1 + m)
            st.session_state.cbs = st.session_state.cusd * t

    # --- ENTRADA DE DATOS ---
    cod = st.text_input("Scanner / Código de Barras:").strip()
    
    if cod and st.session_state.get('last_cod') != cod:
        try:
            p = supabase.table("productos").select("*").eq("codigo", cod).execute()
            if p.data:
                prod = p.data[0]
                st.session_state.update({
                    'nom': prod['nombre'], 'cbs': float(prod['costo_bs']),
                    'cusd': float(prod['costo_usd']), 'mar': float(prod['margen']),
                    'last_cod': cod
                })
                recalcular("cusd")
        except: pass

    st.text_input("Nombre del Producto:", key="nom")
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Costo Bs:", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
        st.number_input("Margen %:", key="mar", on_change=recalcular, args=("mar",), step=1.0)
    with col2:
        st.number_input("Costo USD:", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
        st.number_input("Venta Bs:", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

    if st.button("💾 GUARDAR CAMBIOS", use_container_width=True, type="primary"):
        try:
            datos = {
                "codigo": cod, "nombre": st.session_state.nom,
                "costo_bs": st.session_state.cbs, "costo_usd": st.session_state.cusd,
                "margen": st.session_state.mar, "venta_bs": st.session_state.vbs
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("¡Guardado!")
        except Exception as e:
            st.error(f"Error: {e}")
