import streamlit as st

def mostrar(supabase):
    # Estilos para replicar tu interfaz de escritorio (Botón Rojo y Cuadro Verde)
    st.markdown("""
        <style>
        .stButton>button { background-color: #ff4b4b; color: white; width: 100%; font-weight: bold; height: 50px; }
        .venta-bs-box { background-color: #d4edda; border: 2px solid #28a745; padding: 15px; border-radius: 10px; text-align: center; }
        .venta-bs-price { color: #155724; font-size: 32px; font-weight: bold; margin: 0; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📦 MODULO DE INVENTARIO")

    # --- LÓGICA DE TASA (ID: 1 como en tu código) ---
    tasa_actual = 40.0
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res.data:
            tasa_actual = float(res.data[0]['valor'])
    except: pass

    st.info(f"Tasa de Cambio: {tasa_actual} Bs/$")

    # --- ESTADO DE VARIABLES (Igual a tu self.ent_...) ---
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':25.0, 'vbs':0.0, 'nom':"", 'last_cod': ""})

    # --- FÓRMULAS EXACTAS (Copiadas de tu lógica de escritorio) ---
    def recalcular(origen):
        t = tasa_actual
        m = st.session_state.mar / 100
        if origen == "cbs":
            st.session_state.cusd = st.session_state.cbs / t
            st.session_state.vbs = (st.session_state.cusd * (1 + m)) * t
        elif origen == "cusd":
            st.session_state.cbs = st.session_state.cusd * t
            st.session_state.vbs = (st.session_state.cusd * (1 + m)) * t
        elif origen == "vbs":
            # Inversa: Sacamos el costo desde el precio de venta
            vusd_temp = st.session_state.vbs / t
            st.session_state.cusd = vusd_temp / (1 + m)
            st.session_state.cbs = st.session_state.cusd * t
        elif origen == "mar":
            st.session_state.vbs = (st.session_state.cusd * (1 + m)) * t

    # --- INTERFAZ GRÁFICA ESPEJO ---
    # 1. Código de Barras
    cod = st.text_input("CÓDIGO DE BARRAS", value=st.session_state.get('last_cod', ""), help="Escanee o escriba el código")

    # Búsqueda automática (Copia fiel de tu cargar_datos_guardados)
    if cod and st.session_state.last_cod != cod:
        try:
            p = supabase.table("productos").select("*").eq("codigo", cod).execute()
            if p.data:
                prod = p.data[0]
                st.session_state.update({
                    'nom': prod['nombre'],
                    'cbs': float(prod.get('costo_bs', 0)),
                    'cusd': float(prod.get('costo_usd', 0)),
                    'mar': float(prod.get('margen', 25)),
                    'last_cod': cod
                })
                recalcular("cusd")
            else:
                st.session_state.last_cod = cod # Para no repetir búsqueda si no existe
        except: pass

    # 2. Nombre del Producto
    st.text_input("NOMBRE DEL PRODUCTO", key="nom")

    # 3. Columnas de Costos (Igual a tu grid de escritorio)
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("COSTO BS (FIJO)", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
        st.number_input("MARGEN %", key="mar", on_change=recalcular, args=("mar",), step=1.0)
    with col2:
        st.number_input("COSTO $ (REPOSICIÓN)", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
        st.number_input("VENTA BS (MANUAL)", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

    # 4. Cuadro de Visualización de Venta (El "Label" verde de tu app)
    st.markdown(f"""
        <div class="venta-bs-box">
            <span style="color: #155724; font-size: 14px;">PRECIO DE VENTA FINAL</span><br>
            <p class="venta-bs-price">Bs. {st.session_state.vbs:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # Espaciador

    # 5. Botón de Guardar (El rojo de tu diseño)
    if st.button("💾 GUARDAR CAMBIOS EN INVENTARIO"):
        if not cod or not st.session_state.nom:
            st.warning("⚠️ El código y el nombre son obligatorios")
            return
            
        try:
            datos = {
                "codigo": cod,
                "nombre": st.session_state.nom,
                "costo_bs": st.session_state.cbs,
                "costo_usd": st.session_state.cusd,
                "margen": st.session_state.mar,
                "venta_bs": st.session_state.vbs
            }
            supabase.table("productos").upsert(datos).execute()
            st.success(f"✅ Producto '{st.session_state.nom}' guardado con éxito.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
