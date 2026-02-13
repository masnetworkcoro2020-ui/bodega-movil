import streamlit as st

def mostrar(supabase):
    st.markdown("### 📦 MODULO DE INVENTARIO")

    # --- OBTENER TASA (ID:1 EXACTO A TU CÓDIGO) ---
    tasa = 40.0
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res.data:
            tasa = float(res.data[0]['valor'])
    except: pass

    # --- INICIALIZACIÓN DE CAMPOS (Tus variables originales) ---
    if 'cbs' not in st.session_state:
        st.session_state.update({
            'cbs': 0.0, 'cusd': 0.0, 'mar': 25.0, 
            'vusd': 0.0, 'vbs': 0.0, 'nom': "", 'last_cod': ""
        })

    # --- TU FUNCIÓN RECALCULAR (Copia fiel de tu código original) ---
    def recalcular(tipo):
        t = tasa
        m = st.session_state.mar / 100
        if tipo == "cbs":
            st.session_state.cusd = st.session_state.cbs / t
            st.session_state.vusd = st.session_state.cusd * (1 + m)
            st.session_state.vbs = st.session_state.vusd * t
        elif tipo == "cusd":
            st.session_state.cbs = st.session_state.cusd * t
            st.session_state.vusd = st.session_state.cusd * (1 + m)
            st.session_state.vbs = st.session_state.vusd * t
        elif tipo == "vbs":
            st.session_state.vusd = st.session_state.vbs / t
            st.session_state.cusd = st.session_state.vusd / (1 + m)
            st.session_state.cbs = st.session_state.cusd * t
        elif tipo == "vusd":
            st.session_state.vbs = st.session_state.vusd * t
            st.session_state.cusd = st.session_state.vusd / (1 + m)
            st.session_state.cbs = st.session_state.cusd * t
        elif tipo == "mar":
            st.session_state.vusd = st.session_state.cusd * (1 + m)
            st.session_state.vbs = st.session_state.vusd * t

    # --- INTERFAZ DE USUARIO (Tus campos originales) ---
    cod = st.text_input("CÓDIGO DE BARRAS", value=st.session_state.last_cod)

    # Búsqueda automática (Tu función cargar_datos_guardados)
    if cod and st.session_state.last_cod != cod:
        try:
            p = supabase.table("productos").select("*").eq("codigo", cod).execute()
            if p.data:
                prod = p.data[0]
                st.session_state.update({
                    'nom': prod.get('nombre', ""),
                    'cbs': float(prod.get('costo_bs', 0)),
                    'cusd': float(prod.get('costo_usd', 0)),
                    'mar': float(prod.get('margen', 25)),
                    'last_cod': cod
                })
                recalcular("cusd")
        except: pass

    st.text_input("NOMBRE DEL PRODUCTO", key="nom")

    # Los 5 campos de tu fórmula 360° en el orden de tu UI
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("COSTO BS", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
        st.number_input("COSTO $", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
        st.number_input("MARGEN %", key="mar", on_change=recalcular, args=("mar",), step=1.0)
    
    with c2:
        st.number_input("VENTA $", key="vusd", on_change=recalcular, args=("vusd",), format="%.2f")
        st.number_input("VENTA BS", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

    st.write("")
    # Botón de Guardar (Tu lógica de upsert)
    if st.button("💾 GUARDAR/ACTUALIZAR EN INVENTARIO", use_container_width=True):
        try:
            datos = {
                "codigo": cod, 
                "nombre": st.session_state.nom,
                "costo_bs": st.session_state.cbs, 
                "costo_usd": st.session_state.cusd,
                "margen": st.session_state.mar, 
                "venta_usd": st.session_state.vusd,
                "venta_bs": st.session_state.vbs
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("✅ ¡Cambios guardados!")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
