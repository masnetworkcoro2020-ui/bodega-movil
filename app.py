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
        # Buscamos el valor en tu tabla ajustes, ID 1 (el que usa tu PC)
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

def actualizar_tasa_db(nueva_tasa):
    try:
        supabase.table("ajustes").update({"valor": nueva_tasa}).eq("id", 1).execute()
        return True
    except: return False

def verificar_clave(clave_ingresada):
    try:
        # Busca en la tabla 'usuarios' (ajusta el nombre si es diferente)
        res = supabase.table("usuarios").select("*").eq("password", clave_ingresada).execute()
        return len(res.data) > 0
    except: return False

# --- LÓGICA DE TASA ---
tasa = obtener_tasa()

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""
if 'calc' not in st.session_state: st.session_state.calc = {}

# --- BLOQUEO DE SEGURIDAD ---
if not st.session_state.autenticado:
    st.title("🔐 Royal Essence Access")
    clave = st.text_input("Introduce clave maestra:", type="password")
    if st.button("Entrar"):
        if verificar_clave(clave):
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("❌ Clave inválida.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.sidebar.title("Royal Essence")
st.sidebar.metric("Tasa Actual", f"{tasa} Bs/$")

menu = ["📸 Escáner", "🛒 Registrar Venta", "📝 Gestión 360°", "📋 Historial", "📦 Inventario", "⚙️ Ajustes"]
opcion = st.sidebar.radio("Menú", menu)

# --- SECCIÓN NUEVA: AJUSTES (CAMBIAR TASA) ---
if opcion == "⚙️ Ajustes":
    st.subheader("Configuración del Sistema")
    st.write("Aquí puedes cambiar la tasa del dólar para que afecte a toda la app y a la PC.")
    
    nueva_tasa_input = st.number_input("Nueva Tasa Bs/$:", value=tasa, format="%.2f", step=0.10)
    
    if st.button("🚀 ACTUALIZAR TASA EN TODA LA RED"):
        if actualizar_tasa_db(nueva_tasa_input):
            st.success(f"✅ Tasa actualizada a {nueva_tasa_input} Bs. ¡Ya cambió en la PC también!")
            st.balloons()
            st.rerun()
        else:
            st.error("No se pudo actualizar la tasa.")

# --- 1. ESCÁNER ---
elif opcion == "📸 Escáner":
    st.subheader("Escanear Código")
    foto = st.camera_input("Enfoca el producto")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            lectura = codigos[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Detectado: {st.session_state.codigo_escaneado}")
            st.info("Pasa a 'Venta' o 'Gestión'.")

# --- 2. REGISTRAR VENTA ---
elif opcion == "🛒 Registrar Venta":
    st.subheader("Nueva Venta")
    cod_v = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    if cod_v:
        res = supabase.table("productos").select("*").eq("codigo", cod_v).execute()
        if res.data:
            p = res.data[0]
            st.write(f"### {p['nombre']}")
            
            # Recalculamos la venta en Bs con la tasa fresca
            v_usd = p['venta_usd']
            v_bs_fresca = v_usd * tasa
            
            c1, c2 = st.columns(2)
            c1.metric("Precio $", f"{v_usd:.2f}")
            c2.metric("Precio Bs", f"{v_bs_fresca:.2f}")
            
            cant = st.number_input("Cantidad", min_value=1, value=1)
            if st.button("Confirmar Venta"):
                # Registrar historial
                supabase.table("historial_ventas").insert({
                    "producto": p['nombre'], "cantidad": cant, 
                    "total_usd": v_usd * cant, "fecha": datetime.now().isoformat()
                }).execute()
                # Restar existencia
                if 'existencia' in p:
                    supabase.table("productos").update({"existencia": p['existencia'] - cant}).eq("identifi", p['identifi']).execute()
                st.success("¡Venta completada!")
                st.session_state.codigo_escaneado = ""
        else: st.error("No encontrado.")

# --- 3. GESTIÓN 360 ---
elif opcion == "📝 Gestión 360°":
    # Aquí iría el algoritmo 360 que ya perfeccionamos antes
    st.subheader("Algoritmo 360°")
    # (Poner aquí la lógica del mensaje anterior)

# --- 4. HISTORIAL E INVENTARIO ---
elif opcion == "📋 Historial":
    res = supabase.table("historial_ventas").select("*").order("fecha", desc=True).limit(20).execute()
    if res.data: st.table(pd.DataFrame(res.data)[['fecha', 'producto', 'cantidad', 'total_usd']])

elif opcion == "📦 Inventario":
    res = supabase.table("productos").select("codigo, nombre, venta_usd, existencia").execute()
    if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)

if st.sidebar.button("Salir"):
    st.session_state.autenticado = False
    st.rerun()
