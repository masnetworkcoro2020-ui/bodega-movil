import streamlit as st
import pandas as pd

def mostrar(supabase):
    st.markdown("<h3 style='text-align: center;'>📦 CALCULADORA DE INVENTARIO 360</h3>", unsafe_allow_html=True)
    
    # 1. OBTENER TASA (Tu ID:1 original)
    tasa = 1.0
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res_tasa.data:
            tasa = float(res_tasa.data[0]['valor'])
    except: tasa = 40.0

    # Inicializar el estado de los campos si no existen
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':25.0, 'vusd':0.0, 'vbs':0.0, 'nom':""})

    # --- LÓGICA DE RECÁLCULO (IGUAL A TU FUNCIÓN recalcular() DE PC) ---
    def actualizar(origen):
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

    # --- DISEÑO DE ENTRADA (Mismos colores de tu PC) ---
    with st.container():
        # Escáner nativo rápido
        foto = st.camera_input("📷 ESCANEAR CÓDIGO")
        cod = st.text_input("Código de Barras", key="cod_actual").strip().upper()

        if cod:
            # Si el código cambia, cargamos datos de la DB
            if 'last_cod' not in st.session_state or st.session_state.last_cod != cod:
                res = supabase.table("productos").select("*").eq("codigo", cod).execute()
                if res.data:
                    p = res.data[0]
                    st.session_state.update({
                        'nom': p.get('nombre', ""), 'cbs': float(p.get('costo_bs', 0)),
                        'cusd': float(p.get('costo_usd', 0)), 'mar': float(p.get('margen', 25)),
                        'last_cod': cod
                    })
                    actualizar("cusd")

        st.text_input("Nombre del Producto", key="nom")

        # Fila 1: Costos (Tus colores: Amarillo y Gris)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<label style='color: #f1c40f;'>Costo Bs. (Fijo)</label>", unsafe_allow_html=True)
            st.number_input("", key="cbs", format="%.2f", on_change=actualizar, args=("cbs",), label_visibility="collapsed")
        with c2:
            st.markdown("<label style='color: #85929e;'>Costo $ (Reposición)</label>", unsafe_allow_html=True)
            st.number_input("", key="cusd", format="%.2f", on_change=actualizar, args=("cusd",), label_visibility="collapsed")

        # Fila 2: Margen y Venta $
        c3, c4 = st.columns(2)
        with c3:
            st.number_input("Margen %", key="mar", step=1.0, on_change=actualizar, args=("mar",))
        with c4:
            st.number_input("Venta $", key="vusd", format="%.2f", disabled=True)

        # Fila 3: VENTA BS (Tu cuadro Verde grande)
        st.markdown(f"""
            <div style='background-color: #d4efdf; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #27ae60;'>
                <p style='color: black; margin: 0; font-weight: bold;'>VENTA BS. (MÓVIL)</p>
                <h1 style='color: #1e8449; margin: 0;'>Bs. {st.session_state.vbs:.2f}</h1>
            </div>
        """, unsafe_allow_html=True)
        # Campo oculto para que el usuario pueda forzar el precio en Bs si quiere
        st.number_input("Ajustar Venta Bs. manualmente:", key="vbs", on_change=actualizar, args=("vbs",))

    # --- BOTONERA ---
    st.write("")
    if st.button("💾 GUARDAR CAMBIOS EN DB", use_container_width=True, type="primary"):
        datos = {
            "codigo": cod, "nombre": st.session_state.nom,
            "costo_bs": st.session_state.cbs, "costo_usd": st.session_state.cusd,
            "margen": st.session_state.mar, "venta_usd": st.session_state.vusd,
            "venta_bs": st.session_state.vbs
        }
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Sincronizado con la Bodega! ✅")

    # --- TU TREEVIEW (Tabla completa) ---
    with st.expander("📋 VER TODO EL INVENTARIO"):
        res_all = supabase.table("productos").select("*").order("nombre").execute()
        if res_all.data:
            df = pd.DataFrame(res_all.data)
            # Reordenamos como tu Treeview
            cols_ok = ["codigo", "nombre", "costo_bs", "costo_usd", "margen", "venta_usd", "venta_bs"]
            st.dataframe(df[cols_ok], use_container_width=True)
