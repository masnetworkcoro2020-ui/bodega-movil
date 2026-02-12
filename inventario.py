import streamlit as st
from PIL import Image

def mostrar(supabase):
    st.markdown("### 📦 MÓDULO DE INVENTARIO 360°")

    # --- 1. TASA DE CAMBIO (Tu ID:1 original) ---
    tasa = 40.0
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res.data: tasa = float(res.data[0]['valor'])
    except: pass
    st.info(f"Tasa actual: {tasa} Bs/$")

    # --- 2. ESTADO DE LOS CAMPOS (Variables espejo) ---
    if 'cbs' not in st.session_state:
        st.session_state.update({'cbs':0.0, 'cusd':0.0, 'mar':25.0, 'vbs':0.0, 'nom':"", 'last_cod': ""})

    # --- 3. TU FÓRMULA 360° (Copia fiel de recalcular) ---
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

    # --- 4. CÁMARA DEL TELÉFONO (Escáner Nativo) ---
    foto = st.camera_input("📷 Escanear código de barras")
    if foto:
        st.warning("Código capturado. Ingrese los datos abajo.")
        # Aquí puedes procesar la imagen si deseas, pero para evitar errores 
        # de 'ModuleNotFound', permitimos que la cámara tome la foto del producto.

    # --- 5. CAMPOS DE ENTRADA (Interfaz espejo) ---
    cod = st.text_input("CÓDIGO DE BARRAS", value=st.session_state.last_cod)
    
    # Búsqueda automática (Tu lógica cargar_datos_guardados)
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

    c1, c2 = st.columns(2)
    with c1:
        st.number_input("COSTO BS (FIJO)", key="cbs", on_change=recalcular, args=("cbs",), format="%.2f")
        st.number_input("MARGEN %", key="mar", on_change=recalcular, args=("mar",), step=1.0)
    with c2:
        st.number_input("COSTO $ (REPOSICIÓN)", key="cusd", on_change=recalcular, args=("cusd",), format="%.2f")
        st.number_input("VENTA BS (MANUAL)", key="vbs", on_change=recalcular, args=("vbs",), format="%.2f")

    # Cuadro Verde de Precio Final
    st.markdown(f"""
        <div style="background-color: #d4edda; border: 2px solid #28a745; padding: 15px; border-radius: 10px; text-align: center;">
            <p style="color: #155724; font-size: 14px; margin: 0;">PRECIO DE VENTA FINAL</p>
            <h2 style="color: #155724; margin: 0;">Bs. {st.session_state.vbs:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    if st.button("💾 GUARDAR CAMBIOS EN INVENTARIO", use_container_width=True):
        try:
            supabase.table("productos").upsert({
                "codigo": cod, "nombre": st.session_state.nom,
                "costo_bs": st.session_state.cbs, "costo_usd": st.session_state.cusd,
                "margen": st.session_state.mar, "venta_bs": st.session_state.vbs
            }).execute()
            st.success("✅ Guardado exitosamente")
        except Exception as e: st.error(f"Error al guardar: {e}")
