import streamlit as st
from config import conectar
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Ventas - Lyan", layout="centered")
supabase = conectar()

# 1. Obtener Tasa Actualizada
res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa = float(res_t.data[0]['valor']) if res_t.data else 40.0

st.title("🛒 Carrito de Ventas")
st.sidebar.metric("Tasa de Cobro", f"{tasa} Bs/$")

# Inicializar el carrito en la memoria si no existe
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- BUSCADOR / ESCÁNER ---
# Si vienes de escaneas en app.py, el código ya debería estar aquí
cod_vender = st.text_input("🔍 Escanee o escriba el código:", value=st.session_state.get('codigo_escaneado', ""))

if st.button("➕ Agregar al Carrito") and cod_vender:
    res_p = supabase.table("productos").select("*").eq("codigo", cod_vender).execute()
    
    if res_p.data:
        prod = res_p.data[0]
        # Agregamos al carrito con el precio que tú calculaste en el 360
        item = {
            "id_prod": prod['identifi'],
            "nombre": prod['nombre'],
            "precio_usd": prod['venta_usd'],
            "precio_bs": prod['venta_bs'],
            "cantidad": 1
        }
        st.session_state.carrito.append(item)
        st.session_state.codigo_escaneado = "" # Limpiamos el bolsillo
        st.success(f"Agregado: {prod['nombre']}")
        st.rerun()
    else:
        st.error("Producto no encontrado. Regístralo en el Inventario primero.")

# --- MOSTRAR CARRITO ---
if st.session_state.carrito:
    st.write("### Productos a cobrar:")
    df_carro = pd.DataFrame(st.session_state.carrito)
    st.table(df_carro[["nombre", "precio_usd", "precio_bs"]])

    total_usd = sum(item['precio_usd'] for item in st.session_state.carrito)
    total_bs = sum(item['precio_bs'] for item in st.session_state.carrito)

    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("TOTAL A COBRAR $", f"{total_usd:.2f} $")
    c2.metric("TOTAL A COBRAR BS", f"{total_bs:.2f} Bs")

    metodo = st.selectbox("Método de Pago", ["Efectivo $", "Efectivo Bs", "Pago Móvil", "Punto de Venta", "Zelle"])

    if st.button("✅ FINALIZAR VENTA"):
        # Guardamos cada item en la tabla 'ventas' para el historial
        for item in st.session_state.carrito:
            venta_data = {
                "producto_id": item['id_prod'],
                "monto_usd": item['precio_usd'],
                "monto_bs": item['precio_bs'],
                "metodo": metodo,
                "fecha": datetime.now().isoformat()
            }
            supabase.table("ventas").insert(venta_data).execute()
        
        st.session_state.carrito = [] # Vaciamos el carrito
        st.balloons()
        st.success("Venta registrada exitosamente.")
        st.rerun()

    if st.button("🗑️ Vaciar Carrito"):
        st.session_state.carrito = []
        st.rerun()
