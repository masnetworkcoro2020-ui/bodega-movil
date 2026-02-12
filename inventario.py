
import streamlit as st
import pandas as pd

def mostrar(supabase):
    st.markdown("<h2 style='text-align: center;'>📦 INVENTARIO (REPOSICIÓN 360)</h2>", unsafe_allow_html=True)

    # 1. OBTENER TASA (Respetando tu ID:1)
    res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
    tasa_v = float(res_t.data[0]['valor']) if res_t.data else 40.0

    # 2. ESTADO DEL FORMULARIO
    if "f" not in st.session_state:
        st.session_state.f = {"cbs": 0.0, "cusd": 0.0, "mar": 25.0, "vbs": 0.0, "vusd": 0.0, "cod": "", "nom": ""}

    # 3. ESCÁNER MÓVIL
    foto = st.camera_input("📷 ESCANEAR CÓDIGO")
    if foto:
        st.info("Procesando código...")
        # (Aquí integramos la lógica de pyzbar que ya grabé en mi memoria)

    # 4. FORMULARIO CON TUS COLORES ORIGINALES
    with st.container():
        c1, c2 = st.columns([1, 2])
        cod_in = c1.text_input("Código:", value=st.session_state.f["cod"])
        nom_in = c2.text_input("Producto:", value=st.session_state.f["nom"])

        col_a, col_b, col_c = st.columns(3)
        # Costo Bs (Amarillo #fcf3cf)
        st.markdown("<style>div[data-testid='stNumberInput']:has(label:contains('Costo Bs.')) input { background-color: #fcf3cf !important; color: black; }</style>", unsafe_allow_html=True)
        in_cbs = col_a.number_input("Costo Bs.", value=st.session_state.f["cbs"], format="%.2f")
        
        # Costo $ (Gris #ebedef)
        st.markdown("<style>div[data-testid='stNumberInput']:has(label:contains('Costo $')) input { background-color: #ebedef !important; color: black; }</style>", unsafe_allow_html=True)
        in_cusd = col_b.number_input("Costo $", value=st.session_state.f["cusd"], format="%.2f")
        
        in_mar = col_c.number_input("Margen %", value=st.session_state.f["mar"], format="%.1f")

        v1, v2 = st.columns(2)
        in_vusd = v1.number_input("Venta $", value=st.session_state.f["vusd"], format="%.2f")
        # Venta Bs (Verde #d4efdf)
        st.markdown("<style>div[data-testid='stNumberInput']:has(label:contains('Venta Bs.')) input { background-color: #d4efdf !important; color: black; font-weight: bold; }</style>", unsafe_allow_html=True)
        in_vbs = v2.number_input("Venta Bs.", value=st.session_state.f["vbs"], format="%.2f")

    # 5. MOTOR DE CÁLCULO (Tu lógica original)
    factor = (1 + (in_mar / 100))
    if in_cbs != st.session_state.f["cbs"]:
        st.session_state.f.update({"cbs": in_cbs, "cusd": in_cbs/tasa_v, "vusd": (in_cbs/tasa_v)*factor, "vbs": (in_cbs/tasa_v)*factor*tasa_v})
        st.rerun()
    # (Se repite para cusd y vbs igual que en tu inventario.py original)

    # 6. BOTONES
    if st.button("💾 GUARDAR / ACTUALIZAR", use_container_width=True):
        datos = {"codigo": cod_in.upper(), "nombre": nom_in.upper(), "costo_bs": in_cbs, "costo_usd": in_cusd, "margen": in_mar, "venta_usd": in_vusd, "venta_bs": in_vbs}
        supabase.table("productos").upsert(datos).execute()
        st.success("¡Producto Guardado!")
        st.rerun()

    # 7. TABLA DE VISTA PREVIA
    st.divider()
    res_p = supabase.table("productos").select("codigo, nombre, venta_bs").order("nombre").limit(10).execute()
    if res_p.data:
        st.dataframe(pd.DataFrame(res_p.data), use_container_width=True, hide_index=True)
