# --- 2. ESCÁNER MULTIMODAL ---
    st.info("💡 Tip: Mantén el producto a 20cm de distancia para que enfoque bien.")
    
    opcion_escaneo = st.radio("Método de entrada:", ["Cámara en vivo", "Subir foto / Galería"], horizontal=True)

    codigo_detectado = None

    if opcion_escaneo == "Cámara en vivo":
        foto = st.camera_input("📷 ENFOCA EL CÓDIGO")
        if foto:
            with st.spinner('Procesando...'):
                codigo_detectado = lector.procesar_escaneo(foto)
    else:
        archivo = st.file_uploader("📁 Selecciona una foto nítida del código", type=['jpg', 'png', 'jpeg'])
        if archivo:
            with st.spinner('Analizando archivo...'):
                codigo_detectado = lector.procesar_escaneo(archivo)

    # Lógica de respuesta al detectar código
    if codigo_detectado:
        st.session_state.f["cod"] = codigo_detectado
        # Búsqueda en Supabase
        res_b = supabase.table("productos").select("*").eq("codigo", codigo_detectado).execute()
        if res_b.data:
            p = res_b.data[0]
            st.session_state.f.update({
                "nom": p['nombre'], "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
                "mar": float(p['margen']), "vbs": float(p['venta_bs']), "vusd": float(p['venta_usd'])
            })
            st.success(f"✅ ¡Leído!: {p['nombre']}")
        else:
            st.warning(f"🆕 Nuevo: {codigo_detectado}")
        st.rerun()
    elif foto if 'foto' in locals() else None:
        st.error("❌ No se pudo leer. Intenta alejar un poco el teléfono o usa 'Subir foto'.")
