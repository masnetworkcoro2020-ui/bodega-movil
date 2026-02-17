import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd
from datetime import datetime

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Pro", layout="centered")
supabase = conectar()

# --- FUNCIONES NÚCLEO ---
def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

def actualizar_tasa_db(nueva_tasa):
    try:
        supabase.table("ajustes").update({"valor": nueva_tasa}).eq("id", 1).execute()
        return True
    except: return False

def verificar_acceso(user_input, pass_input):
    try:
        # Verificamos contra tu tabla 'usuarios'
        res = supabase.table("usuarios").select("*").eq("usuario", user_input).eq("clave", pass_input).execute()
        return res.data[0] if res.data else None
    except: return None

# --- INICIALIZACIÓN ---
tasa = obtener_tasa()
if 'auth' not in st.session_state: st.session_state.auth = None
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""
if 'calc' not in st.session_state: st.session_state.calc = {}

# --- PANTALLA DE LOGIN ---
if not st.session_state.auth:
    st.title("🔐 Royal Essence - Acceso")
    u = st.text_input("Usuario (Ej: marianela, jmaar):").lower()
    p = st.text_input("Clave:", type="password")
    if st.button("Iniciar Sesión"):
        usuario_valido = verificar_acceso(u, p)
        if usuario_valido:
            st.session_state.auth = usuario_valido
            st.success(f"Bienvenido/a {usuario_valido['usuario']}")
            st.rerun()
        else:
            st.error("Credenciales incorrectas, mano.")
    st.stop()

# --- INTERFAZ POST-LOGIN ---
st.sidebar.title(f"👤 {st.session_state.auth['usuario'].upper()}")
st.sidebar.metric("Tasa Actual", f"{tasa} Bs/$")

menu = ["📸 Escáner", "🛒 Vender", "📝 Gestión 360°", "📋 Historial", "⚙️ Ajustes"]
opcion = st.sidebar.radio("Menú", menu)

# --- ⚙️ AJUSTES (CAMBIAR TASA) ---
if opcion == "⚙️ Ajustes":
    st.subheader("Configuración de Tasa")
    nueva_tasa = st.number_input("Editar Tasa BCV:", value=tasa, format="%.2f", step=0.1)
    if st.button("Actualizar Tasa en todo el Sistema"):
        if actualizar_tasa_db(nueva_tasa):
            st.success(f"Tasa cambiada a {nueva_tasa}. ¡Sincronizado con la PC!")
            st.rerun()

# --- 📸 ESCÁNER ---
elif opcion == "📸 Escáner":
    st.subheader("Escaneo de Barras")
    foto = st.camera_input("Enfoca el producto")
    if foto:
        img = Image.open(foto)
        detect = decode(img)
        if detect:
            raw = detect[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = raw[1:] if len(raw) == 13 and raw.startswith('0') else raw
            st.success(f"Código: {st.session_state.codigo_escaneado}")
            st.info("Ahora ve a 'Vender' o 'Gestión 360°'")

# --- 🛒 VENDER ---
elif opcion == "🛒 Vender":
    st.subheader("Punto de Venta Móvil")
    cod = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    if cod:
        res = supabase.table("productos").select("*").eq("codigo", cod).execute()
        if res.data:
            p = res.data[0]
            st.write(f"### {p['nombre']}")
            st.metric("Precio Final", f"{p['venta_bs']:.2f} Bs", f"{p['venta_usd']} $")
            
            cant = st.number_input("Cantidad", min_value=1, value=1)
            if st.button("💸 REGISTRAR VENTA"):
                # Guardamos en historial
                supabase.table("historial_ventas").insert({
                    "producto": p['nombre'], "cantidad": cant, 
                    "total_usd": p['venta_usd'] * cant, 
                    "vendedor": st.session_state.auth['usuario'],
                    "fecha": datetime.now().isoformat()
                }).execute()
                st.success("Venta guardada.")
                st.session_state.codigo_escaneado = ""
        else: st.error("Producto no registrado.")

# --- 📝 GESTIÓN 360° (ALGORITMO TOTAL) ---
elif opcion == "📝 Gestión 360°":
    st.subheader("Cerebro de Precios 360°")
    cod_g = st.text_input("Código para gestionar:", value=st.session_state.codigo_escaneado)
    if cod_g:
        res = supabase.table("productos").select("*").eq("codigo", cod_g).execute()
        prod = res.data[0] if res.data else {}
        
        with st.form("brain_360"):
            nombre = st.text_input("Nombre", value=prod.get('nombre', ''))
            margen = st.number_input("Margen %", value=float(prod.get('margen', 30.0)))
            st.write("---")
            c1, c2 = st.columns(2)
            in_cbs = c1.number_input("Costo Bs", value=0.0)
            in_cusd = c2.number_input("Costo USD", value=0.0)
            in_vbs = c1.number_input("Venta Bs", value=0.0)
            in_vusd = c2.number_input("Venta USD", value=0.0)
            
            if st.form_submit_button("🧮 CALCULAR Y GUARDAR"):
                m = margen / 100
                # Lógica de prioridad de entrada
                if in_cbs > 0: c_bs, c_usd = in_cbs, in_cbs/tasa; v_usd = c_usd*(1+m); v_bs = v_usd*tasa
                elif in_cusd > 0: c_usd, c_bs = in_cusd, in_cusd*tasa; v_usd = c_usd*(1+m); v_bs = v_usd*tasa
                elif in_vbs > 0: v_bs, v_usd = in_vbs, in_vbs/tasa; c_usd = v_usd/(1+m); c_bs = c_usd*tasa
                elif in_vusd > 0: v_usd, v_bs = in_vusd, in_vusd*tasa; c_usd = v_usd/(1+m); c_bs = c_usd*tasa
                else: st.error("Mete al menos un precio, mano."); st.stop()

                datos = {
                    "codigo": cod_g, "nombre": nombre.upper(), "margen": margen,
                    "costo_bs": c_bs, "costo_usd": c_usd, "venta_bs": v_bs, "venta_usd": v_usd
                }
                if prod: supabase.table("productos").update(datos).eq("identifi", prod['identifi']).execute()
                else: supabase.table("productos").insert(datos).execute()
                st.success("Sincronizado 360°")

# --- 📋 HISTORIAL ---
elif opcion == "📋 Historial":
    st.subheader("Últimas Ventas")
    res = supabase.table("historial_ventas").select("*").order("fecha", desc=True).limit(20).execute()
    if res.data: st.dataframe(pd.DataFrame(res.data)[['fecha', 'producto', 'total_usd', 'vendedor']])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = None
    st.rerun()
