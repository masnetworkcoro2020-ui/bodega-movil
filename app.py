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
            # LECTURA EXACTA: No agregamos ni quitamos nada
            codigo = codigos[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = codigo
            
            st.success(f"✅ Código detectado: {codigo}")
            st.info("El código ya está listo en 'Venta' o 'Inventario'.")
        else:
            st.warning("No se pudo leer. Intenta centrar bien el código de barras.")

# --- OPCIÓN 2: VENTAS (Búsqueda Exacta) ---
elif opcion == "🛒 Registrar Venta":
    st.subheader("Registrar Salida")
    
    # El código aparece tal cual se leyó
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        # Buscamos la coincidencia exacta en la columna 'codigo'
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        
        if res.data:
            p = res.data[0]
            st.write(f"### {p['nombre']}")
            st.metric("Precio", f"$ {p['venta_usd']}")
            
            if p['existencia'] > 0:
                if st.button("Confirmar Venta (-1 unidad)"):
                    nuevo_stock = p['existencia'] - 1
                    supabase.table("productos").update({"existencia": nuevo_stock}).eq("id", p['id']).execute()
                    st.success(f"Venta de {p['nombre']} registrada. Quedan {nuevo_stock}.")
                    st.session_state.codigo_escaneado = "" # Limpiamos para el siguiente
            else:
                st.error("⚠️ No hay stock disponible.")
        else:
            st.error(f"El código {cod_actual} no existe. Ve a 'Agregar' para registrarlo.")

# --- OPCIÓN 3: AGREGAR NUEVO ---
elif opcion == "📝 Agregar al Inventario":
    st.subheader("Entrada de Mercancía")
    
    with st.form("registro"):
        # El código aparece exacto aquí también
        cod_form = st.text_input("Código:", value=st.session_state.codigo_escaneado)
        nombre = st.text_input("Nombre del producto:")
        precio = st.number_input("Precio USD:", min_value=0.0, format="%.2f")
        stock = st.number_input("Cantidad inicial:", min_value=1)
        
        if st.form_submit_button("Guardar en Supabase"):
            if cod_form and nombre:
                supabase.table("productos").insert({
                    "codigo": cod_form, 
                    "nombre": nombre.upper(), 
                    "venta_usd": precio, 
                    "existencia": stock
                }).execute()
                st.success(f"✅ {nombre} guardado con código {cod_form}")
                st.session_state.codigo_escaneado = "" # Limpiamos
            else:
                st.warning("Faltan datos obligatorios.")
