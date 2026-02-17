import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Móvil", layout="centered")
supabase = conectar()

if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Royal Essence - Bodega")

# --- MENÚ LATERAL ---
menu = ["📸 Escáner", "🛒 Ventas", "📦 Inventario Completo"]
opcion = st.sidebar.radio("Menú:", menu)

# --- OPCIÓN 1: ESCÁNER ---
if opcion == "📸 Escáner":
    st.subheader("Paso 1: Escanear Código")
    foto = st.camera_input("Enfoca el producto")
    
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        
        if codigos:
            lectura_raw = codigos[0].data.decode('utf-8').strip()
            # Limpieza exacta para códigos de 12 dígitos
            codigo_final = lectura_raw[1:] if len(lectura_raw) == 13 and lectura_raw.startswith('0') else lectura_raw
            
            st.session_state.codigo_escaneado = codigo_final
            st.success(f"✅ Código detectado: {codigo_final}")
            st.info("Pasa a la pestaña 'Ventas' ahora.")
        else:
            st.warning("No se leyó nada. Intenta con más luz o acerca más el cel.")

# --- OPCIÓN 2: VENTAS ---
elif opcion == "🛒 Ventas":
    st.subheader("Registro de Salida")
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        try:
            # CAMBIO AQUÍ: Nombre de tabla "productos" (con S)
            res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
            
            if res.data:
                p = res.data[0]
                nombre = p.get('nombre', 'Sin Nombre')
                precio = p.get('venta_usd', 0.0)
                
                # Buscamos la columna de stock. Si no existe 'existencia', el sistema no se cae.
                stock = p.get('existencia', 0) 

                st.markdown(f"### ✨ {nombre}")
                col1, col2 = st.columns(2)
                col1.metric("Precio USD", f"$ {precio}")
                col2.metric("Stock actual", f"{stock} und")
                
                if st.button(f"REGISTRAR VENTA"):
                    # Solo restamos si hay stock o si decides vender en negativo
                    nuevo_stock = int(stock) - 1
                    supabase.table("productos").update({"existencia": nuevo_stock}).eq("identificador", p['identificador']).execute()
                    st.success(f"Vendido. Stock: {nuevo_stock}")
                    st.session_state.codigo_escaneado = ""
            else:
                st.error(f"El código {cod_actual} no está en la tabla 'productos'.")
        except Exception as e:
            st.error(f"Error técnico: {e}")

# --- OPCIÓN 3: INVENTARIO ---
elif opcion == "📦 Inventario Completo":
    st.subheader("Existencias en Nube")
    try:
        # CAMBIO AQUÍ: Nombre de tabla "productos" (con S)
        res = supabase.table("productos").select("codigo, nombre, venta_usd, existencia").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar: {e}")
