import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd
from datetime import datetime

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence ERP", layout="centered")
supabase = conectar()

# --- FUNCIONES DE APOYO ---
def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

def verificar_clave(clave_ingresada):
    try:
        # Busca en la tabla 'usuarios' una clave que coincida
        res = supabase.table("usuarios").select("*").eq("password", clave_ingresada).execute()
        return len(res.data) > 0
    except: return False

tasa = obtener_tasa()

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""
if 'calc' not in st.session_state: st.session_state.calc = {}

# --- BLOQUEO DE SEGURIDAD ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso Restringido")
    clave = st.text_input("Introduce tu clave de acceso:", type="password")
    if st.button("Entrar"):
        if verificar_clave(clave):
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Clave incorrecta. Intenta de nuevo.")
    st.stop()

# --- SI ESTÁ AUTENTICADO, MUESTRA EL MENÚ ---
st.sidebar.title("Royal Essence")
st.sidebar.metric("Tasa BCV", f"{tasa} Bs/$")

menu = ["📸 Escáner", "🛒 Registrar Venta", "📝 Gestión 360°", "📋 Historial", "📦 Inventario"]
opcion = st.sidebar.radio("Menú Principal", menu)

# --- 1. ESCÁNER ---
if opcion == "📸 Escáner":
    st.subheader("Escanear Producto")
    foto = st.camera_input("Enfoca el código")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            lectura = codigos[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Detectado: {st.session_state.codigo_escaneado}")
            st.info("Ahora selecciona 'Venta' o 'Gestión' en el menú.")

# --- 2. VENTAS ---
elif opcion == "🛒 Registrar Venta":
    st.subheader("Nueva Venta")
    cod_v = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    if cod_v:
        res = supabase.table("productos").select("*").eq("codigo", cod_v).execute()
        if res.data:
            p = res.data[0]
            st.write(f"### {p['nombre']}")
            colv1, colv2 = st.columns(2)
            colv1.metric("Precio USD", f"{p['venta_usd']} $")
            colv2.metric("Precio Bs", f"{p['venta_bs']} Bs")
            
            cant = st.number_input("Cantidad", min_value=1, value=1)
            total_v = p['venta_usd'] * cant
            st.write(f"**Total a cobrar: {total_v:.2f} $ ({total_v*tasa:.2f} Bs)**")
            
            if st.button("Confirmar Venta"):
                # 1. Registrar en Historial
                venta_data = {
                    "producto": p['nombre'],
                    "cantidad": cant,
                    "total_usd": total_v,
                    "fecha": datetime.now().isoformat()
                }
                supabase.table("historial_ventas").insert(venta_data).execute()
                # 2. Restar Stock (si tienes la columna)
                if 'existencia' in p:
                    nuevo_s = p['existencia'] - cant
                    supabase.table("productos").update({"existencia": nuevo_s}).eq("identifi", p['identifi']).execute()
                
                st.success("¡Venta registrada con éxito!")
                st.session_state.codigo_escaneado = ""
        else: st.error("Producto no encontrado.")

# --- 3. GESTIÓN 360° (TU ALGORITMO) ---
elif opcion == "📝 Gestión 360°":
    st.subheader("Cerebro 360°")
    # ... (Aquí va todo el código del Algoritmo 360 que hicimos en el paso anterior)
    # [Insertar aquí la lógica de cálculo que ya tienes]
    st.write("Usa esta pestaña para modificar precios o agregar nuevos.")

# --- 4. HISTORIAL ---
elif opcion == "📋 Historial":
    st.subheader("Ventas Recientes")
    try:
        res = supabase.table("historial_ventas").select("*").order("fecha", desc=True).limit(20).execute()
        if res.data:
            df_h = pd.DataFrame(res.data)
            st.table(df_h[['fecha', 'producto', 'cantidad', 'total_usd']])
    except: st.warning("Aún no hay ventas registradas.")

# --- 5. INVENTARIO ---
elif opcion == "📦 Inventario":
    st.subheader("Stock Completo")
    res = supabase.table("productos").select("codigo, nombre, venta_usd, existencia").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()
