import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# Configuración Inicial
st.set_page_config(page_title="Inversiones Lyan", layout="centered")
supabase = conectar()

# --- SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso - Inversiones Lyan")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # Buscamos en tu tabla 'usuarios'
        res = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("clave", clave).execute()
        
        if res.data:
            st.session_state.autenticado = True
            st.session_state.user_data = res.data[0]
            st.success(f"Bienvenido {res.data[0]['nombre']}")
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
    st.stop() # Detiene el resto del código si no está logueado

# --- SI LLEGA AQUÍ, ES PORQUE SE LOGUEÓ ---

def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa = obtener_tasa()

if 'codigo_escaneado' not in st.session_state: 
    st.session_state.codigo_escaneado = ""

# Encabezado con Logout
col_t, col_l = st.columns([4, 1])
col_t.title("🔄 Gestión 360°")
if col_l.button("Salir"):
    st.session_state.autenticado = False
    st.rerun()

st.sidebar.metric("Tasa de Cambio", f"{tasa} Bs/$")
st.sidebar.write(f"👤: {st.session_state.user_data['nombre']}")

# --- SECCIÓN 1: ESCÁNER ---
st.subheader("📸 Escaneo Rápido")
foto = st.camera_input("Enfoca el código de barras")
if foto:
    imagen = Image.open(foto)
    codigos = decode(imagen)
    if codigos:
        lectura = codigos[0].data.decode('utf-8').strip()
        st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
        st.success(f"✅ Código: {st.session_state.codigo_escaneado}")

st.divider()

# --- SECCIÓN 2: EL CEREBRO 360 ---
st.subheader("📝 Edición de Producto")
cod_actual = st.text_input("Código:", value=st.session_state.codigo_escaneado)

if cod_actual:
    res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
    p = res.data[0] if res.data else {}
    
    if p: st.info(f"📍 Editando: {p.get('nombre')}")
    else: st.warning("✨ Producto Nuevo")

    nombre = st.text_input("Nombre", value=p.get('nombre', ''))
    margen = st.number_input("Ganancia %", value=float(p.get('margen', 25.0)), step=1.0)
    
    col1, col2 = st.columns(2)
    in_cbs = col1.number_input("Costo Bs", value=0.0)
    in_cusd = col2.number_input("Costo $", value=0.0)
    in_vbs = col1.number_input("Venta Bs", value=0.0)
    in_vusd = col2.number_input("Venta $", value=0.0)

    # Lógica Matemática 360
    m = margen / 100
    c_bs, c_usd, v_bs, v_usd = 0.0, 0.0, 0.0, 0.0

    if in_cbs > 0:
        c_bs = in_cbs; c_usd = c_bs / tasa; v_usd = c_usd * (1 + m); v_bs = v_usd * tasa
    elif in_cusd > 0:
        c_usd = in_cusd; c_bs = c_usd * tasa; v_usd = c_usd * (1 + m); v_bs = v_usd * tasa
    elif in_vbs > 0:
        v_bs = in_vbs; v_usd = v_bs / tasa; c_usd = v_usd / (1 + m); c_bs = c_usd * tasa
    elif in_vusd > 0:
        v_usd = in_vusd; v_bs = v_usd * tasa; c_usd = v_usd / (1 + m); c_bs = c_usd * tasa
    else:
        c_usd = float(p.get('costo_usd', 0.0)); c_bs = float(p.get('costo_bs', 0.0))
        v_usd = float(p.get('venta_usd', 0.0)); v_bs = v_usd * tasa

    with st.container(border=True):
        st.write("### 📊 Precios Finales")
        r1, r2 = st.columns(2)
        r1.metric("VENTA BS", f"{v_bs:.2f}")
        r2.metric("VENTA USD", f"{v_usd:.2f} $")

    if st.button("💾 GUARDAR TODO"):
        datos = {
            "codigo": cod_actual, "nombre": nombre.upper(), "costo_bs": round(c_bs, 2),
            "costo_usd": round(c_usd, 2), "margen": margen, "venta_usd": round(v_usd, 2), "venta_bs": round(v_bs, 2)
        }
        if p: supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
        else: supabase.table("productos").insert(datos).execute()
        st.success("✅ ¡Sincronizado!")
        st.session_state.codigo_escaneado = ""
