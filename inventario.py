import streamlit as st
import pandas as pd
import lector # Importamos el archivo que creamos antes

def mostrar(supabase):
    st.markdown("<h2 style='text-align: center;'>📦 GESTIÓN DE INVENTARIO</h2>", unsafe_allow_html=True)

    # 1. OBTENER TASA (ID:1)
    try:
        res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0
    except: tasa_v = 40.0

    # Inicializar el formulario si está vacío
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

    # --- 2. EL BLOQUE QUE ME MOSTRASTE (ESCÁNER) ---
    foto = st.camera_input("📷 ESCANEAR CÓDIGO")
    
    if foto:
        codigo = lector.procesar_escaneo(foto)
        if codigo:
            st.session_state.f["cod"] = codigo
            # Buscamos de una vez si el producto existe
            res_b = supabase.table("productos").select("*").eq("codigo", codigo).execute()
            if res_b.data:
                p = res_b.data[0]
                st.session_state.f.update({
                    "nom": p['nombre'], "cbs": float(p['costo_bs']), "cusd": float(p['costo_usd']),
                    "mar": float(p['margen']), "vbs": float(p['venta_bs']), "vusd": float(p['venta_usd'])
                })
                st.success(f"✅ Producto: {p['nombre']}")
            else:
                st.warning(f"🆕 Código nuevo: {codigo}")
            st.rerun()
        else:
            st.error("⚠️ No se pudo leer el código. Intenta con más luz.")

    # --- 3. DISEÑO DE ENTRADA (Colores de tu programa original) ---
    st.markdown("""
        <style>
        div[data-testid="stNumberInput"]:has(label:contains("Costo Bs.")) input { background-color: #fcf3cf !important; }
        div[data-testid="stNumberInput"]:has(label:contains("Venta Bs.")) input { background-color: #d4efdf !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    cod_in = st.text_input("Código:", value=st.session_state.f["cod"])
    nom_in = st.text_input("Producto:", value=st.session_state.f["nom"]).upper()

    col1, col2, col3 = st.columns(3)
    in_cbs = col1.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
    in_cusd = col2.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
    in_mar = col3.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")

    col4, col5 = st.columns(2)
    in_vusd = col4.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
    in_vbs = col5.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # --- 4. MOTOR 360 (Recalculo automático) ---
    factor = (1 + (in_mar / 100))
    if in_cbs != st.session_state.f["cbs"]:
        st.session_state.f.update({"cbs": in_cbs, "cusd": in_cbs/tasa_v, "vusd": (in_cbs/tasa_v)*factor, "vbs": (in_cbs/tasa_v)*factor*tasa_v})
        st.rerun()
    elif in_cusd != st.session_state.f["cusd"]:
        st.session_state.f.update({"cusd": in_cusd, "cbs": in_cusd*tasa_v, "vusd": in_cusd*factor, "vbs": in_cusd*factor*tasa_v})
        st.rerun()

    if st.button("💾 GUARDAR CAMBIOS", use_container_width=True):
        datos = {"codigo": cod_in, "nombre": nom_in, "costo_bs": in_cbs, "costo_usd": in_cusd, "margen": in_mar, "venta_usd": in_vusd, "venta_bs": in_vbs}
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Guardado en la nube!")
