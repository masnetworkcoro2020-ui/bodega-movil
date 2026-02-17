import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Bodega Móvil Pro", layout="centered")
supabase = conectar()

# --- EL BOLSILLO MÁGICO (Session State) ---
if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Bodega Pro")

# --- MENÚ LATERAL ---
menu = ["📸 Escáner Rápido", "🛒 Registrar Venta", "📝 Agregar al Inventario"]
opcion = st.sidebar.radio("Ir a:", menu)

# --- OPCIÓN 1: EL ESCÁNER ---
if opcion == "📸 Escáner Rápido":
    st.subheader("Paso 1: Escanea el producto")
    foto = st.camera_input("Enfoca el código")
    
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        
        if codigos:
            # Guardamos el código en el "bolsillo"
            codigo = codigos[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = codigo
            
            st.success(f"✅ Código {codigo} capturado.")
            st.info("Ahora ve a 'Venta' o 'Inventario' en el menú, ¡ya el código te está esperando allá!")
        else:
            st.warning("No se leyó nada, intenta otra vez.")

# --- OPCIÓN 2: VENTAS ---
elif opcion == "🛒 Registrar Venta":
    st.subheader("Registrar Salida")
    
    # Aquí el código aparece solo porque lo sacamos del "bolsillo"
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        if res.data:
            p = res.data[0]
            st.write(f"### {p['nombre']}")
            st.metric("Precio", f"$ {p['venta_usd']}")
            if st.button("Confirmar Venta (-1 unidad)"):
                # Aquí restamos stock
                nuevo_stock = p['existencia'] - 1
                supabase.table("productos").update({"existencia": nuevo_stock}).eq("id", p['id']).execute()
                st.success("¡Venta registrada!")
                st.session_state.codigo_escaneado = "" # Limpiamos el bolsillo después de vender
        else:
            st.error("Producto no encontrado. ¿Deseas registrarlo?")

# --- OPCIÓN 3: AGREGAR NUEVO ---
elif opcion == "📝 Agregar al Inventario":
    st.subheader("Entrada de Mercancía")
    
    # El código también aparece aquí solito
    with st.form("registro"):
        cod_form = st.text_input("Código:", value=st.session_state.codigo_escaneado)
        nombre = st.text_input("Nombre del producto:")
        precio = st.number_input("Precio USD:", min_value=0.0)
        stock = st.number_input("Cantidad:", min_value=1)
        
        if st.form_submit_button("Guardar en Nube"):
            # Lógica para insertar en Supabase
            supabase.table("productos").insert({
                "codigo": cod_form, "nombre": nombre.upper(), 
                "venta_usd": precio, "existencia": stock
            }).execute()
            st.success("¡Guardado!")
            st.session_state.codigo_escaneado = "" # Limpiamos
