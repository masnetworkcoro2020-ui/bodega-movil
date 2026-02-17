import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar  # Importamos tu conexión pro
import pandas as pd

# Configuración de la página para que se vea bien en el cel
st.set_page_config(page_title="Bodega Móvil - Escáner", layout="centered")

st.title("📱 Escáner de Bodega")

# Conectamos a Supabase
supabase = conectar()

# El disparador de la cámara
foto = st.camera_input("Enfoca el código de barras del producto")

if foto:
    # 1. Procesar la imagen
    imagen = Image.open(foto)
    codigos = decode(imagen)
    
    if not codigos:
        st.warning("No se detectó ningún código. Intenta enfocar mejor o con más luz.")
    
    for objeto in codigos:
        codigo_detectado = objeto.data.decode('utf-8')
        # Limpiamos el código (a veces traen ceros extra)
        cod_limpio = codigo_detectado.strip().lstrip('0')
        cod_con_cero = "0" + cod_limpio

        st.info(f"🔍 Buscando código: {codigo_detectado}")

        # 2. Buscar en Supabase (buscamos el código tal cual y con el cero adelante)
        try:
            res = supabase.table("productos")\
                .select("*")\
                .or_(f"codigo.eq.{cod_limpio},codigo.eq.{cod_con_cero}")\
                .execute()

            if res.data:
                p = res.data[0]
                st.success(f"✅ ¡Producto Encontrado!")
                
                # 3. Mostrar la ficha del producto elegante
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Producto", p['nombre'])
                    st.metric("Precio USD", f"$ {p['venta_usd']}")
                with col2:
                    st.metric("Stock", f"{p['existencia']} unid.")
                    # Calculamos el precio en bolívares (asumiendo que tienes la tasa)
                    # Aquí podrías traer la tasa de la tabla ajustes
                    st.write(f"**Categoría:** {p.get('categoria', 'General')}")
                
                # Botón rápido para vender (opcional)
                if st.button(f"Registrar venta de {p['nombre']}"):
                    st.write("Registrando...") # Aquí iría la lógica de restar stock
            else:
                st.error(f"❌ El código {codigo_detectado} no está registrado en la base de datos.")
                if st.button("➕ Registrar como producto nuevo"):
                    st.write("Formulario para agregar producto...")

        except Exception as e:
            st.error(f"Error de conexión: {e}")

# Tabla de inventario rápido abajo para referencia
if st.checkbox("Ver todo el inventario"):
    res_total = supabase.table("productos").select("nombre, venta_usd, existencia").execute()
    df = pd.DataFrame(res_total.data)
    st.table(df)
