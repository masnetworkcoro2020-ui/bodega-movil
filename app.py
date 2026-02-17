import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

st.set_page_config(page_title="Bodega Móvil Pro", layout="centered")
supabase = conectar()

st.title("🛒 Control de Inventario")

# --- MENÚ DE OPCIONES ---
opcion = st.sidebar.radio("Ir a:", ["Escanear / Vender", "Agregar Producto Nuevo", "Ver Inventario"])

if opcion == "Escanear / Vender":
    foto = st.camera_input("Escanea para buscar o vender")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        
        if codigos:
            codigo_detectado = codigos[0].data.decode('utf-8').strip()
            st.info(f"Código: {codigo_detectado}")
            
            # Buscamos en Supabase
            res = supabase.table("productos").select("*").eq("codigo", codigo_detectado).execute()
            
            if res.data:
                p = res.data[0]
                st.success(f"Producto: {p['nombre']}")
                st.metric("Existencia", f"{p['existencia']} und")
                # Aquí puedes poner el botón de restar stock que hicimos antes
            else:
                st.error("⚠️ Este producto no existe en el inventario.")
                st.info("Copia este código y ve a 'Agregar Producto Nuevo' en el menú lateral.")
                st.code(codigo_detectado) # Para que lo copies fácil

elif opcion == "Agregar Producto Nuevo":
    st.header("📝 Registro de Nuevo Producto")
    
    with st.form("form_nuevo"):
        nuevo_codigo = st.text_input("Código de Barras (Escaneado o manual)")
        nuevo_nombre = st.text_input("Nombre del Producto (Ej: Perfume Hugo Boss)")
        nuevo_precio = st.number_input("Precio en USD $", min_value=0.0, step=0.5)
        nueva_existencia = st.number_input("Cantidad que llegó", min_value=1, step=1)
        
        btn_guardar = st.form_submit_button("Guardar en Supabase")
        
        if btn_guardar:
            if nuevo_codigo and nuevo_nombre:
                data_insert = {
                    "codigo": nuevo_codigo,
                    "nombre": nuevo_nombre.upper(),
                    "venta_usd": nuevo_precio,
                    "existencia": nueva_existencia
                }
                # ENVIAR A SUPABASE
                try:
                    supabase.table("productos").insert(data_insert).execute()
                    st.success(f"✅ ¡{nuevo_nombre} agregado con éxito!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Mano, llena el nombre y el código por lo menos.")

elif opcion == "Ver Inventario":
    st.header("📦 Stock en la Nube")
    res = supabase.table("productos").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df)
