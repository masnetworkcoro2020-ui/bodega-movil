import streamlit as st
import pandas as pd

def mostrar(supabase):
    st.markdown("<h3 style='text-align: center;'>📦 INVENTARIO INVERSIONES LYAN</h3>", unsafe_allow_html=True)
    
    # 1. OBTENER TASA (ID:1)
    tasa_actual = 1.0
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res_tasa.data:
            tasa_actual = float(res_tasa.data[0]['valor'])
    except: pass

    st.info(f"📊 Tasa del Sistema: **Bs. {tasa_actual}**")

    # 2. ESCÁNER / ENTRADA DE DATOS
    with st.expander("📷 ABRIR CÁMARA PARA ESCANEAR", expanded=True):
        st.camera_input("Enfoca el código de barras")
    
    codigo_input = st.text_input("Ingresa o pega el código aquí:", key="input_movil_final")
    codigo_final = codigo_input.strip()

    if codigo_final:
        try:
            # Búsqueda con el nombre exacto de tu columna: 'codigo'
            res = supabase.table("productos").select("*").eq("codigo", codigo_final).execute()

            if res.data:
                p = res.data[0]
                st.success(f"✅ PRODUCTO: {p.get('nombre')}")
                
                # --- PANEL DE EDICIÓN ---
                col1, col2 = st.columns(2)
                with col1:
                    # Costo Bs Fijo (Tu lógica de PC)
                    c_bs = st.number_input("Costo Bs. (Fijo)", value=float(p.get('costo_bs', 0)), format="%.2f")
                    # Margen
                    margen = st.number_input("Margen %", value=float(p.get('margen', 25)), step=1.0)
                
                with col2:
                    # Costo USD
                    c_usd = st.number_input("Costo $", value=float(p.get('costo_usd', 0)), format="%.2f")
                    # Cálculo automático de Venta USD
                    v_usd = c_usd * (1 + (margen / 100))
                    st.metric("Venta $", f"$ {v_usd:.2f}")

                # PANEL VENTA BS (Tu color verde de éxito)
                v_bs = v_usd * tasa_actual
                st.markdown(f"""
                    <div style='background-color: #d4efdf; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #27ae60;'>
                        <p style='color: black; margin: 0; font-weight: bold;'>VENTA AL PÚBLICO</p>
                        <h1 style='color: #1e8449; margin: 0;'>Bs. {v_bs:.2f}</h1>
                    </div>
                """, unsafe_allow_html=True)

                st.write("")
                if st.button("💾 ACTUALIZAR BODEGA", use_container_width=True, type="primary"):
                    datos = {
                        "costo_bs": c_bs,
                        "costo_usd": c_usd,
                        "margen": margen,
                        "venta_usd": v_usd,
                        "venta_bs": v_bs
                    }
                    supabase.table("productos").update(datos).eq("codigo", codigo_final).execute()
                    st.balloons()
                    st.toast("¡Producto actualizado!", icon="🚀")
            else:
                st.error("❌ Código no encontrado. Verifica si el producto existe.")
        except Exception as e:
            st.error(f"Error de base de datos: {e}")

    # 3. TABLA DE CONSULTA RÁPIDA
    st.divider()
    if st.checkbox("📋 Mostrar lista de productos"):
        try:
            res_all = supabase.table("productos").select("nombre, codigo, venta_bs").limit(10).execute()
            if res_all.data:
                st.dataframe(pd.DataFrame(res_all.data), use_container_width=True)
        except: pass
