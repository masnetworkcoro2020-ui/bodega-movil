import streamlit as st
import pandas as pd

def mostrar(supabase):
    # 1. TASA DESDE LA DB (ID:1 como el original)
    tasa = 1.0
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res.data:
            tasa = float(res.data[0]['valor'])
    except: tasa = 40.0

    # INICIALIZAR VARIABLES DE CÁLCULO (Tu lógica 360)
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':30.0, 'vusd':0.0, 'vbs':0.0})

    # FUNCIÓN DE RECÁLCULO (Copia exacta de tu lógica de PC)
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

    st.markdown(f"### 🧮 Calculadora 360° (Tasa: {tasa})")

    # BÚSQUEDA
    cod = st.text_input("Código de Barras", key="main_cod").strip()
    
    if cod:
        res = supabase.table("productos").select("*").eq("codigo", cod).execute()
        if res.data:
            p = res.data[0]
            # Carga inicial de datos
            if st.session_state.get('last_cod') != cod:
                st.session_state.update({
                    'nom': p['nombre'], 'cbs': float(p['costo_bs']),
                    'cusd': float(p['costo_usd']), 'mar': float(p['margen']),
                    'last_cod': cod
                })
                recalcular("cusd")

            st.text_input("Nombre del Producto", key="nom")

            # --- LOS CAMPOS CON FÓRMULAS ---
            col1, col2 = st.columns(2)
            with col1:
                # COSTO BS -> Dispara Costo USD y Ventas
                st.number_input("Costo Bs.", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
                # MARGEN % -> Dispara Ventas
                st.number_input("Margen %", key="mar", on_change=recalcular, args=("mar",), step=1.0)
            
            with col2:
                # COSTO USD -> Dispara Costo Bs y Ventas
                st.number_input("Costo USD ($)", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
                # VENTA USD (Calculado)
                st.number_input("Venta USD ($)", key="vusd", format="%.2f", disabled=True)

            # VENTA BS (El campo maestro)
            st.number_input("VENTA PÚBLICO BS.", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

            # BOTÓN DE GUARDADO (Para mandar los cálculos a la nube)
            if st.button("💾 SINCRONIZAR CON BODEGA", use_container_width=True, type="primary"):
                datos = {
                    "costo_bs": st.session_state.cbs, "costo_usd": st.session_state.cusd,
                    "margen": st.session_state.mar, "venta_usd": st.session_state.vusd,
                    "venta_bs": st.session_state.vbs
                }
                supabase.table("productos").update(datos).eq("codigo", cod).execute()
                st.success("¡Datos guardados!")

    # TREEVIEW (Visualización rápida)
    with st.expander("📊 Vista de Tabla"):
        res_all = supabase.table("productos").select("codigo,nombre,venta_bs").limit(20).execute()
        if res_all.data:
            st.dataframe(pd.DataFrame(res_all.data), use_container_width=True)
