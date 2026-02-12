import streamlit as st
import pandas as pd

def mostrar(supabase):
    st.markdown("<h3 style='text-align: center;'>📦 GESTIÓN DE INVENTARIO 360</h3>", unsafe_allow_html=True)
    
    # 1. OBTENER TASA ACTUAL (ID:1)
    tasa_actual = 1.0
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res_tasa.data:
            tasa_actual = float(res_tasa.data[0]['valor'])
    except: pass

    st.warning(f"📊 TASA ACTUAL: **Bs. {tasa_actual}**")

    # 2. SECCIÓN DE ENTRADA (Cámara y Manual)
    with st.expander("📷 ABRIR ESCÁNER", expanded=True):
        st.camera_input("Enfoca el código")
    
    codigo_input = st.text_input("Código de Barras:", key="cod_final").strip()

    if codigo_input:
        try:
            # Buscamos con el nombre de columna exacto 'codigo'
            res = supabase.table("productos").select("*").eq("codigo", codigo_input).execute()

            if res.data:
                p = res.data[0]
                st.success(f"📍 Producto: {p.get('nombre')}")
                
                # --- LÓGICA DE PROTECCIÓN DE REPOSICIÓN (RÉPLICA PC) ---
                col1, col2 = st.columns(2)
                
                with col1:
                    # COSTO BS (El que fijas en tienda - Amarillo)
                    st.markdown("**Costo Bs (Fijo)**")
                    c_bs = st.number_input("Bs.", value=float(p.get('costo_bs', 0)), format="%.2f", key="c_bs")
                    
                    # MARGEN (Tu porcentaje de ganancia)
                    st.markdown("**Margen %**")
                    margen = st.number_input("%", value=float(p.get('margen', 25)), step=1.0, key="margen")

                with col2:
                    # COSTO USD (Para reposición - Gris)
                    st.markdown("**Costo USD ($)**")
                    c_usd = st.number_input("$", value=float(p.get('costo_usd', 0)), format="%.2f", key="c_usd")
                    
                    # CÁLCULO DE VENTA USD
                    # venta_usd = costo_usd * (1 + margen/100)
                    v_usd = c_usd * (1 + (margen / 100))
                    st.metric("Venta USD", f"$ {v_usd:.2f}")

                # --- EL CORAZÓN: VENTA AL PÚBLICO BS ---
                # Fórmula: venta_bs = venta_usd * tasa_actual
                v_bs = v_usd * tasa_actual
                
                # Estilo visual idéntico a tu "Verde" de Venta
                st.markdown(f"""
                    <div style='background-color: #d4efdf; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #27ae60; margin-top: 15px;'>
                        <p style='color: black; margin: 0; font-weight: bold; font-size: 1.1em;'>PRECIO DE VENTA (BS)</p>
                        <h1 style='color: #1e8449; margin: 0; font-size: 2.5em;'>Bs. {v_bs:.2f}</h1>
                        <p style='color: #555; font-size: 0.8em; margin-top: 5px;'>Protección contra devaluación activa ✅</p>
                    </div>
                """, unsafe_allow_html=True)

                st.write("")
                if st.button("💾 GUARDAR CAMBIOS EN BODEGA", use_container_width=True, type="primary"):
                    # Actualizamos con los nombres exactos de tu tabla en Supabase
                    datos_upd = {
                        "costo_bs": c_bs,
                        "costo_usd": c_usd,
                        "margen": margen,
                        "venta_usd": v_usd,
                        "venta_bs": v_bs
                    }
                    supabase.table("productos").update(datos_upd).eq("codigo", codigo_input).execute()
                    st.balloons()
                    st.toast("¡Base de datos sincronizada!", icon="🔥")
            else:
                st.error("❌ Código no encontrado en el sistema.")

        except Exception as e:
            st.error(f"Error técnico: {e}")

    # 3. LISTADO RÁPIDO DE PRECIOS
    st.divider()
    with st.expander("🔍 Consultar Precios Rápidos"):
        res_list = supabase.table("productos").select("nombre, codigo, venta_bs").limit(15).execute()
        if res_list.data:
            st.dataframe(pd.DataFrame(res_list.data), use_container_width=True)
