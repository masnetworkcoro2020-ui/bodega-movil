import streamlit as st
from config import conectar # Usamos tu conexión original

# Configuración para que se vea bien en el teléfono
st.set_page_config(page_title="Bodega Pro Móvil", page_icon="🏪")

st.title("🏪 Mi Bodega Pro")
st.write("---")

# Conectamos usando tu función de config.py
supabase = conectar()

if supabase:
    try:
        # 1. Traer la Tasa BCV (de tu tabla 'ajustes')
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        tasa = float(res_tasa.data[0]['valor']) if res_tasa.data else 1.0
        
        st.metric(label="Tasa BCV Actual", value=f"Bs. {tasa:,.2f}")

        # 2. Buscador de productos
        busqueda = st.text_input("🔍 Buscar producto por nombre...")

        # 3. Traer Inventario (de tu tabla 'productos')
        query = supabase.table("productos").select("nombre, venta_usd, stock")
        if busqueda:
            query = query.ilike("nombre", f"%{busqueda}%")
        
        res_prod = query.execute()

        if res_prod.data:
            for p in res_prod.data:
                precio_bs = p['venta_usd'] * tasa
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{p['nombre']}**")
                        st.write(f"Stock: {p['stock']}")
                    with col2:
                        st.write(f"**${p['venta_usd']:.2f}**")
                        st.write(f"Bs. {precio_bs:,.2f}")
                    st.write("---")
        else:
            st.info("No hay productos que coincidan.")

    except Exception as e:
        st.error(f"Error al leer datos: {e}")
else:
    st.error("No se pudo conectar con Supabase.")