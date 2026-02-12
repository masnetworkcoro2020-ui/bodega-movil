import streamlit as st
import lector  # Importamos tu nueva herramienta

def mostrar(supabase):
    # ... (tu lógica de tasa y session_state) ...

    # ESCÁNER LIGERO
    foto = st.camera_input("📷 ESCANEAR CÓDIGO")
    
    if foto:
        codigo_detectado = lector.procesar_escaneo(foto)
        
        if codigo_detectado:
            st.session_state.f["cod"] = codigo_detectado
            
            # Buscamos en la nube
            res_b = supabase.table("productos").select("*").eq("codigo", codigo_detectado).execute()
            if res_b.data:
                p = res_b.data[0]
                st.session_state.f.update({
                    "nom": p['nombre'], "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
                    "mar": float(p['margen']), "vbs": float(p['venta_bs']), "vusd": float(p['venta_usd'])
                })
                st.success(f"✅ Encontrado: {p['nombre']}")
            else:
                # Nuevo producto, limpiamos excepto el código
                st.session_state.f.update({"nom": "", "cbs": 0.0, "cusd": 0.0, "vbs": 0.0, "vusd": 0.0})
                st.warning("🆕 Producto nuevo")
            
            st.rerun()
        else:
            st.error("❌ No se pudo leer. Intenta de nuevo.")

    # ... (Resto del formulario y Motor 360) ...
