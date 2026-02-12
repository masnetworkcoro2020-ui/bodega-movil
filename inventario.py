# --- 2. ESCÁNER REPOTENCIADO ---
    foto = st.camera_input("📷 ENFOCA EL CÓDIGO DE BARRAS")
    
    if foto:
        # Mostramos un mensaje de progreso
        with st.spinner('Procesando imagen...'):
            codigo = lector.procesar_escaneo(foto)
            
            if codigo:
                st.session_state.f["cod"] = codigo
                # Búsqueda en Supabase
                res_b = supabase.table("productos").select("*").eq("codigo", codigo).execute()
                if res_b.data:
                    p = res_b.data[0]
                    st.session_state.f.update({
                        "nom": p['nombre'], "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
                        "mar": float(p['margen']), "vbs": float(p['venta_bs']), "vusd": float(p['venta_usd'])
                    })
                    st.success(f"✅ ¡Leído!: {p['nombre']}")
                else:
                    st.warning(f"🆕 Código nuevo detectado: {codigo}")
                st.rerun()
            else:
                # Si falla, damos instrucciones claras al usuario
                st.error("❌ No se detectó el código.")
                st.info("""
                **Tips para que lea rápido:**
                1. **No pegues el celular al producto:** Aléjalo unos 20cm (que se vea el producto completo).
                2. **Espera el foco:** Asegúrate que las rayas negras se vean nítidas en la pantalla antes de disparar.
                3. **Horizontal:** Mantén el código de barras acostado (horizontal).
                """)
