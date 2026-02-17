import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Móvil", layout="centered")
supabase = conectar()

# --- SESIÓN PARA GUARDAR EL CÓDIGO ---
if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Royal Essence - Bodega")

# --- MENÚ LATERAL ---
menu = ["📸 Escáner", "🛒 Ventas", "📦 Inventario Completo"]
opcion = st.sidebar.radio("Menú:", menu)

# --- MÉDULA: ESCÁNER ---
if opcion == "📸 Escáner":
    st.subheader("Paso 1: Escanear Código")
    foto = st.camera_input("Enfoca el perfume o producto")
    
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        
        if codigos:
            lectura_raw = codigos[0].data.decode('utf-8').strip()
            # Limpieza para códigos de 12 dígitos (quita el 0 inicial si pyzbar lo agrega)
            codigo_final = lectura_raw[1:] if len(lectura_raw) == 13 and lectura_raw.startswith('0') else lectura_raw
            
            st.session_state.codigo_escaneado = codigo_final
            st.success(f"✅ Código detectado: {codigo_final}")
            st.info("Ahora ve a la sección 'Ventas' para procesar.")
        else:
            st.warning("No se leyó nada. Prueba con más luz.")

# --- MÉDULA: VENTAS ---
elif opcion == "🛒 Ventas":
    st.subheader("Registro de Salida")
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        try:
            # CORRECCIÓN: La tabla se llama "producto" (en singular)
            res = supabase.table("producto").select("*").eq("codigo", cod_actual).execute()
            
            if res.data:
                p = res.data[0]
                # Extraemos datos según tus nombres exactos
                nombre = p.get('nombre', 'Sin Nombre')
                precio = p.get('venta_usd', 0.0)
                stock = p.get('existencia', 0)

                st.markdown(f"### ✨ {nombre}")
                col1, col2 = st.columns(2)
                col1.metric("Precio USD", f"$ {precio}")
                col2.metric("Stock actual", f"{stock} und")
                
                if stock > 0:
                    if st.button(f"REGISTRAR VENTA"):
                        nuevo_stock = stock - 1
                        # Actualizamos en la tabla "producto"
                        supabase.table("producto").update({"existencia": nuevo_stock}).eq("id", p['id']).execute()
                        st.success(f"¡Vendido! Stock actualizado a {nuevo_stock}")
                        st.session_state.codigo_escaneado = "" # Limpiamos para el siguiente
                else:
                    st.error("⚠️ Producto agotado.")
            else:
                st.error(f"El código {cod_actual} no está en la base de datos.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# --- MÉDULA: INVENTARIO ---
elif opcion == "📦 Inventario Completo":
    st.subheader("Existencias en Nube")
    try:
        res = supabase.table("producto").select("nombre, venta_usd, existencia").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar el inventario: {e}")
