import streamlit as st
import pandas as pd

def mostrar(supabase):
    st.markdown("<h3 style='text-align: center;'>📦 GESTIÓN DE INVENTARIO 360</h3>", unsafe_allow_html=True)
    
    # 1. OBTENER TASA ACTUAL (Usa tu ID:1 original)
    tasa_actual = 40.0
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res_tasa.data:
            tasa_actual = float(res_tasa.data[0]['valor'])
    except: pass

    st.warning(f"Tasa aplicada para cálculos: **Bs. {tasa_actual}**")

    # 2. ESCÁNER NATIVO (Abre la cámara del tlf al instante)
    with st.expander("📷 ABRIR ESCÁNER DE BARRAS", expanded=True):
        foto = st.camera_input("Enfoca el código")
    
    codigo_manual = st.text_input("O ingresa el código manualmente:", key="input_cod")
    
    # El código final será el manual o el que detectemos (puedes escribirlo si la cámara no enfoca)
    codigo_final = codigo_manual.strip().upper()

    if codigo_final:
        try:
            # Buscamos en tu tabla 'productos'
            res = supabase.table("productos").select("*").or_(f"código.eq.{codigo_final},codigo.eq.{codigo_final}").execute()
            
            if res.data:
                p = res.data[0]
                st.success(f"📦 PRODUCTO: {p.get('nombre', 'SIN NOMBRE')}")
                
                # --- PANEL DE EDICIÓN (RÉPLICA DE TU PC) ---
                col1, col2 = st.columns(2)
                
                with col1:
                    # Costo Bs Fijo (Tu color amarillo #fcf3cf)
                    c_bs = st.number_input("Costo Bs. (Fijo)", value=float(p.get('costo_bs', 0)), format="%.2f")
                    # Margen %
                    margen = st.number_input("Margen %", value=float(p.get('margen', 25)), step=1.0)

                with col2:
                    # Costo USD (Tu color gris #ebedef)
                    c_usd = st.number_input("Costo $", value=float(p.get('costo_usd', 0)), format="%.2f")
                    # Venta USD calculada
                    v_usd = c_usd * (1 + (margen / 100))
                    st.metric("Venta $", f"$ {v_usd:.2f}")

                # PANEL DE VENTA BS (Tu color verde #d4efdf)
                v_bs = v_usd * tasa_actual
                st.markdown(f"""
                    <div style='background-color: #d4efdf; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #27ae60;'>
                        <p style='color: black; margin: 0; font-weight: bold;'>VENTA PÚBLICO BS (Móvil)</p>
                        <h1 style='color: #1e8449; margin: 0;'>Bs. {v_bs:.2f}</h1>
                    </div>
                """, unsafe_allow_html=True)

                st.write("")
                if st.button("💾 GUARDAR CAMBIOS EN BODEGA", use_container_width=True, type="primary"):
                    datos = {
                        "costo_bs": c_bs,
                        "costo_usd": c_usd,
                        "margen": margen,
                        "venta_usd": v_usd,
                        "venta_bs": v_bs
                    }
                    # Intentamos guardar con o sin tilde
                    try:
                        supabase.table("productos").update(datos).eq("código", codigo_final).execute()
                    except:
                        supabase.table("productos").update(datos).eq("codigo", codigo_final).execute()
                    
                    st.toast("✅ ¡Actualizado!", icon="🎉")
            else:
                st.error("❌ Código no encontrado en la base de datos.")
        except Exception as e:
            st.error(f"Error: {e}")

    # Tabla de consulta rápida
    with st.expander("📊 Ver Inventario"):
        res_all = supabase.table("productos").select("nombre, código, venta_bs").limit(10).execute()
        if res_all.data:
            st.table(pd.DataFrame(res_all.data))
