import streamlit as st
import pandas as pd

def mostrar(supabase):
    st.markdown("<h3 style='text-align: center;'>📦 INVENTARIO (PROTECCIÓN DE REPOSICIÓN)</h3>", unsafe_allow_html=True)
    
    # 1. OBTENER TASA (Tu ID:1 original)
    tasa = 1.0
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        if res_tasa.data:
            tasa = float(res_tasa.data[0]['valor'])
    except: pass

    # 2. BÚSQUEDA Y ESCÁNER
    with st.expander("📷 ABRIR ESCÁNER / CÁMARA"):
        st.camera_input("Enfoca el código")
    
    cod_buscado = st.text_input("Código de Barras:", key="main_cod").strip().upper()

    if cod_buscado:
        try:
            res = supabase.table("productos").select("*").eq("codigo", cod_buscado).execute()
            if res.data:
                p = res.data[0]
                st.success(f"📍 Producto: {p.get('nombre')}")

                # --- LÓGICA DE RECÁLCULO 360 (IGUAL A TU PC) ---
                # Usamos st.number_input con on_change para imitar tus 'binds'
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # COSTO BS (Amarillo en tu PC)
                    cbs = st.number_input("Costo Bs. (Fijo)", value=float(p.get('costo_bs', 0)), format="%.2f")
                    # MARGEN %
                    margen = st.number_input("Margen %", value=float(p.get('margen', 25)), step=1.0)
                
                with col2:
                    # COSTO USD (Gris en tu PC)
                    # Si el usuario cambia el Costo Bs, tú calculas: cusd = cbs/t
                    cusd_sugerido = cbs / tasa if cbs > 0 else float(p.get('costo_usd', 0))
                    cusd = st.number_input("Costo $ (Reposición)", value=cusd_sugerido, format="%.2f")
                    
                    # VENTA USD (Calculada: vusd = cusd * (1 + m))
                    vusd = cusd * (1 + (margen / 100))
                    st.metric("Venta USD", f"$ {vusd:.2f}")

                # --- EL CORAZÓN: VENTA BS MÓVIL (Verde en tu PC) ---
                # Tu fórmula: vbs = vusd * tasa
                vbs = vusd * tasa
                
                st.markdown(f"""
                    <div style='background-color: #d4efdf; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #27ae60; margin-top: 15px;'>
                        <p style='color: black; margin: 0; font-weight: bold;'>VENTA BS. (MÓVIL)</p>
                        <h1 style='color: #1e8449; margin: 0;'>Bs. {vbs:.2f}</h1>
                        <small style='color: #1e8449;'>Calculado a tasa: {tasa}</small>
                    </div>
                """, unsafe_allow_html=True)

                # --- BOTONERA ---
                st.write("")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("💾 GUARDAR / ACTUALIZAR", use_container_width=True, type="primary"):
                        datos = {
                            "costo_bs": cbs, "costo_usd": cusd, "margen": margen,
                            "venta_usd": vusd, "venta_bs": vbs, "nombre": p.get('nombre')
                        }
                        supabase.table("productos").update(datos).eq("codigo", cod_buscado).execute()
                        st.balloons()
                with col_b2:
                    if st.button("🗑️ ELIMINAR", use_container_width=True):
                        if st.checkbox("Confirmar eliminación"):
                            supabase.table("productos").delete().eq("codigo", cod_buscado).execute()
                            st.experimental_rerun()
            else:
                st.error("❌ Producto no registrado.")
        except Exception as e:
            st.error(f"Error: {e}")

    # 3. TABLA TREEVIEW (Réplica de tu lista)
    st.divider()
    if st.checkbox("📋 Ver Tabla de Inventario"):
        try:
            res_all = supabase.table("productos").select("codigo, nombre, costo_bs, costo_usd, margen, venta_usd, venta_bs").order("nombre").execute()
            if res_all.data:
                df = pd.DataFrame(res_all.data)
                # Renombramos para que se vea como tus headings del Treeview
                df.columns = ["CÓDIGO", "PRODUCTO", "COSTO BS", "COSTO $", "MARGEN %", "VENTA $", "VENTA BS"]
                st.dataframe(df, use_container_width=True)
        except: pass
