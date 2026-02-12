import streamlit as st

def mostrar(supabase):
    st.markdown("<h2 style='text-align: center; color: #3498db;'>🪙 CONFIGURACIÓN DE TASA BCV</h2>", unsafe_allow_html=True)

    # 1. CARGAR TASA ACTUAL (Tal cual como hace tu ModuloTasa)
    try:
        res = supabase.table("ajustes").select("valor").eq("parametro", "tasa_bcv").execute()
        if res.data:
            tasa_actual = float(res.data[0]['valor'])
        else:
            tasa_actual = 0.0
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        tasa_actual = 0.0

    # 2. VISUALIZADOR (El cuadro negro con número grande de tu programa)
    st.markdown(f"""
        <div style="background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; text-align: center; margin-bottom: 20px;">
            <p style="color: gray; margin-bottom: 5px;">VALOR ACTUAL EN SISTEMA</p>
            <h1 style="color: #f1c40f; margin: 0;">Bs. {tasa_actual:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # 3. FORMULARIO DE ACTUALIZACIÓN
    with st.container():
        nueva_tasa = st.number_input("Nueva Tasa (Bs):", value=tasa_actual, format="%.2f", step=0.01)
        
        if st.button("🚀 ACTUALIZAR TASA EN SISTEMA", use_container_width=True):
            try:
                # Actualizamos respetando el parámetro exacto: tasa_bcv
                supabase.table("ajustes").update({"valor": str(nueva_tasa)}).eq("parametro", "tasa_bcv").execute()
                
                st.success(f"✅ Tasa actualizada a Bs. {nueva_tasa}")
                # Forzamos recarga para que el visualizador se actualice
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo guardar: {e}")

    st.info("💡 Nota: Este cambio afectará inmediatamente los cálculos de 'Venta Bs. (Móvil)' en todos los dispositivos.")
