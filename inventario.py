import streamlit as st

def mostrar(supabase):
    # Estilo Espejo: Botón rojo y Cuadro Verde
    st.markdown("""
        <style>
        .stButton>button { background-color: #ff4b4b; color: white; width: 100%; font-weight: bold; }
        .venta-box { background-color: #d4edda; border: 2px solid #28a745; padding: 20px; border-radius: 10px; text-align: center; }
        .venta-text { color: #155724; font-size: 30px; font-weight: bold; margin: 0; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📦 PANEL DE INVENTARIO 360°")

    # 1. Tasa desde DB (ID: 1)
    tasa = 40.0
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res.data: tasa = float(res.data[0]['valor'])
    except: pass

    # Estado de la calculadora (Espejo de tu lógica original)
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':25.0, 'vbs':0.0, 'nom':"", 'last_cod': ""})

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

    # --- INTERFAZ ---
    cod = st.text_input("Código de Barras:").strip()
    
    # Auto-búsqueda espejo
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
        except: pass

    st.text_input("Nombre del Producto:", key="nom")
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Costo Bs. (Fijo):", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
        st.number_input("Margen %:", key="mar", on_change=recalcular, args=("mar",), step=1.0)
    with col2:
        st.number_input("Costo $ (Reposición):", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
        st.number_input("Ajustar Venta Bs. manualmente:", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

    # Cuadro Verde de Venta (El espejo visual)
    st.markdown(f"""
        <div class="venta-box">
            <p style="color: #155724; font-weight: bold; margin-bottom: 5px;">VENTA BS. (MÓVIL)</p>
            <p class="venta-text">Bs. {st.session_state.vbs:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # Espacio

    if st.button("💾 GUARDAR CAMBIOS EN DB"):
        try:
            datos = {
                "codigo": cod, "nombre": st.session_state.nom,
                "costo_bs": st.session_state.cbs, "costo_usd": st.session_state.cusd,
                "margen": st.session_state.mar, "venta_bs": st.session_state.vbs
            }
            supabase.table("productos").upsert(datos).execute()
            st.success("✅ Guardado correctamente en la base de datos.")
        except Exception as e:
            st.error(f"Error: {e}")
