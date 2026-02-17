import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence ERP", layout="centered")
supabase = conectar()

def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa = obtener_tasa()

# --- ESTADO DE SESIÓN ---
# Esto permite que la cámara y el texto se hablen
if 'codigo_escaneado' not in st.session_state: 
    st.session_state.codigo_escaneado = ""

st.title("🔄 Gestión 360° con Escáner")
st.sidebar.metric("Tasa de Cambio", f"{tasa} Bs/$")

menu = ["📸 Escáner", "📝 Gestión 360°", "📦 Inventario"]
opcion = st.sidebar.radio("Ir a:", menu)

# --- 1. ESCÁNER (Paso previo) ---
if opcion == "📸 Escáner":
    st.subheader("Paso 1: Escanear Producto")
    foto = st.camera_input("Enfoca el código de barras")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            # Limpiamos el código (quitamos el 0 inicial si es EAN-13)
            lectura = codigos[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Código capturado: {st.session_state.codigo_escaneado}")
            st.info("Ahora ve a '📝 Gestión 360°' para ver o editar los precios.")
        else:
            st.warning("No se detectó ningún código. Intenta acercar más el producto.")

# --- 2. GESTIÓN 360° (EL CEREBRO) ---
elif opcion == "📝 Gestión 360°":
    st.subheader("Cerebro de Precios")
    
    # Campo de código conectado al escáner
    cod_actual = st.text_input("Código del Producto:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        # Buscamos si ya existe en la nube
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        p = res.data[0] if res.data else {}
        
        if p: st.info(f"📍 Editando: {p.get('nombre')}")
        else: st.warning("✨ Producto nuevo detectado")

        # Entradas principales
        nombre = st.text_input("Nombre del Producto", value=p.get('nombre', ''))
        margen = st.number_input("Margen de Ganancia %", value=float(p.get('margen', 25.0)), step=1.0)
        
        st.markdown("---")
        st.write("💡 **Cálculo Automático:** Escribe en un cuadro y el resto se calculará solo.")
        
        col1, col2 = st.columns(2)
        in_cbs = col1.number_input("Costo Bs (Compra)", value=0.0)
        in_cusd = col2.number_input("Costo $ (Compra)", value=0.0)
        in_vbs = col1.number_input("Venta Final Bs", value=0.0)
        in_vusd = col2.number_input("Venta Final $", value=0.0)

        # --- LÓGICA MATEMÁTICA 360° ---
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
            # Si no hay cambios, muestra los valores actuales de la base de datos
            c_usd = float(p.get('costo_usd', 0.0))
            c_bs = float(p.get('costo_bs', 0.0))
            v_usd = float(p.get('venta_usd', 0.0))
            v_bs = v_usd * tasa

        # Visualización de Resultados
        with st.container(border=True):
            st.write("### 📊 Resultado del Análisis")
            res_col1, res_col2 = st.columns(2)
            res_col1.metric("VENTA BS", f"{v_bs:.2f}")
            res_col1.metric("COSTO BS", f"{c_bs:.2f}")
            res_col2.metric("VENTA USD", f"{v_usd:.2f} $")
            res_col2.metric("COSTO USD", f"{c_usd:.2f} $")

        # --- BOTÓN DE GUARDADO ---
        if st.button("💾 GUARDAR CAMBIOS EN LA NUBE"):
            datos = {
                "codigo": cod_actual,
                "nombre": nombre.upper(),
                "costo_bs": round(c_bs, 2),
                "costo_usd": round(c_usd, 2),
                "margen": margen,
                "venta_usd": round(v_usd, 2),
                "venta_bs": round(v_bs, 2)
            }
            if p: # Si existe, actualiza usando identifi
                supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
            else: # Si es nuevo, inserta
                supabase.table("productos").insert(datos).execute()
            
            st.success("✅ ¡Producto sincronizado perfectamente!")
            st.session_state.codigo_escaneado = "" # Limpiar para el siguiente

# --- 3. INVENTARIO ---
elif opcion == "📦 Inventario":
    st.subheader("Lista de Precios")
    res = supabase.table("productos").select("codigo, nombre, venta_usd, venta_bs").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
