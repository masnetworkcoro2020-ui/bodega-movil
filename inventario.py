import streamlit as st
import pandas as pd
from streamlit_barcode_reader import st_barcode_reader

def mostrar(supabase):
    st.header("📦 GESTIÓN DE INVENTARIO 360")
    
    # 1. OBTENER TASA ACTUAL (Igual que en la PC)
    tasa_actual = 1.0
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res_tasa.data:
            tasa_actual = float(res_tasa.data[0]['valor'])
    except:
        tasa_actual = 1.0

    st.info(f"💡 Tasa de cambio aplicada: **Bs. {tasa_actual}**")

    # 2. ESCÁNER DE RAYO LÁSER
    st.subheader("🔍 Escanear Producto")
    codigo_escaneado = st_barcode_reader(key='barcode_reader')

    # 3. BUSCADOR MANUAL (Por si falla la cámara)
    codigo_manual = st.text_input("o ingresa el código manualmente:", value=codigo_escaneado if codigo_escaneado else "")
    
    codigo_final = codigo_manual if codigo_manual else codigo_escaneado

    if codigo_final:
        try:
            # Buscamos el producto exactamente como en tu tabla 'productos'
            res = supabase.table("productos").select("*").eq("código", codigo_final).execute()
            
            if res.data:
                prod = res.data[0]
                st.success(f"✅ Producto: {prod.get('nombre', 'Sin nombre')}")
                
                # --- FORMULARIO DE EDICIÓN (RÉPLICA DE LA PC) ---
                with st.container():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Precios en USD (Amarillo en tu PC)
                        st.markdown("### 💵 Costos/Venta USD")
                        costo_usd = st.number_input("Costo USD", value=float(prod.get('costo_usd', 0)), format="%.2f")
                        margen = st.number_input("Margen %", value=float(prod.get('margen', 0)), step=1.0)
                        
                        # Cálculo automático de Venta USD
                        venta_usd = costo_usd * (1 + (margen / 100))
                        st.metric("Venta USD", f"$ {venta_usd:.2f}")

                    with col2:
                        # Precios en Bs (Verde en tu PC)
                        st.markdown("### 🇻🇪 Precios Bs")
                        # Fórmulas idénticas a tu código de PC
                        costo_bs = costo_usd * tasa_actual
                        venta_bs = venta_usd * tasa_actual
                        
                        st.metric("Costo Bs", f"Bs. {costo_bs:.2f}")
                        st.write("---")
                        st.metric("VENTA PÚBLICO BS", f"Bs. {venta_bs:.2f}", delta_color="normal")

                    # BOTÓN DE GUARDADO
                    if st.button("💾 GUARDAR CAMBIOS EN BODEGA", use_container_width=True, type="primary"):
                        datos_update = {
                            "costo_usd": costo_usd,
                            "costo_bs": costo_bs,
                            "margen": margen,
                            "venta_usd": venta_usd,
                            "venta_bs": venta_bs
                        }
                        supabase.table("productos").update(datos_update).eq("código", codigo_final).execute()
                        st.balloons()
                        st.success("¡Datos actualizados en tiempo real!")
            else:
                st.error("❌ El código no existe en la base de datos.")
                if st.button("➕ Registrar como nuevo"):
                    st.info("Función para nuevos productos en desarrollo...")
                    
        except Exception as e:
            st.error(f"Error al consultar: {e}")

    # 4. VISTA RÁPIDA DE STOCK (Tabla resumen)
    st.divider()
    if st.checkbox("📊 Ver inventario completo"):
        res_all = supabase.table("productos").select("nombre, código, venta_usd, venta_bs").limit(10).execute()
        if res_all.data:
            df = pd.DataFrame(res_all.data)
            st.dataframe(df, use_container_width=True)
