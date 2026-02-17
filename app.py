import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence 360° Total", layout="centered")
supabase = conectar()

def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute() # Sincronizado con tu ID 1
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa = obtener_tasa()

# --- ESTADO DE LA APP ---
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""
if 'calc' not in st.session_state: st.session_state.calc = {}

st.title("🔄 Algoritmo 360° Total")
st.sidebar.metric("Tasa de Cambio", f"{tasa} Bs/$")

menu = ["📸 Escáner", "📝 Gestión 360°", "📦 Inventario"]
opcion = st.sidebar.radio("Ir a:", menu)

# --- ESCÁNER ---
if opcion == "📸 Escáner":
    st.subheader("Paso 1: Escanear")
    foto = st.camera_input("Enfoca el código")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            lectura = codigos[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Código: {st.session_state.codigo_escaneado}")
            st.info("Pasa a 'Gestión 360°'")

# --- GESTIÓN 360° (EL CEREBRO) ---
elif opcion == "📝 Gestión 360°":
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        p = res.data[0] if res.data else {}
        
        st.markdown(f"### 📋 {p.get('nombre', 'Producto Nuevo')}")
        
        # --- FORMULARIO DE ENTRADA ---
        with st.container(border=True):
            nombre = st.text_input("Nombre del Producto", value=p.get('nombre', ''))
            margen = st.number_input("Margen de Ganancia %", value=float(p.get('margen', 30.0)))
            
            st.write("---")
            st.write("💡 **¿Qué dato tienes ahora?** (Rellena solo uno para calcular el resto)")
            
            col1, col2 = st.columns(2)
            with col1:
                in_cbs = st.number_input("Costo en Bs", value=0.0, format="%.2f")
                in_vbs = st.number_input("Venta Final en Bs", value=0.0, format="%.2f")
            with col2:
                in_cusd = st.number_input("Costo en USD $", value=0.0, format="%.2f")
                in_vusd = st.number_input("Venta Final en USD $", value=0.0, format="%.2f")

            # --- BOTÓN DE CÁLCULO 360 ---
            if st.button("🧮 CALCULAR ALGORITMO 360°"):
                m_dec = margen / 100
                
                # Lógica: Prioridad de cálculo según lo que el usuario escribió
                if in_cbs > 0: # Entró por Costo Bs
                    c_bs, c_usd = in_cbs, in_cbs / tasa
                    v_usd = c_usd * (1 + m_dec)
                    v_bs = v_usd * tasa
                elif in_cusd > 0: # Entró por Costo USD
                    c_usd, c_bs = in_cusd, in_cusd * tasa
                    v_usd = c_usd * (1 + m_dec)
                    v_bs = v_usd * tasa
                elif in_vbs > 0: # Entró por Venta Bs
                    v_bs, v_usd = in_vbs, in_vbs / tasa
                    c_usd = v_usd / (1 + m_dec)
                    c_bs = c_usd * tasa
                elif in_vusd > 0: # Entró por Venta USD
                    v_usd, v_bs = in_vusd, in_vusd * tasa
                    c_usd = v_usd / (1 + m_dec)
                    c_bs = c_usd * tasa
                else:
                    # Si no escribió nada nuevo, usa lo que está en DB
                    c_usd = float(p.get('costo_usd', 0))
                    c_bs = float(p.get('costo_bs', 0))
                    v_usd = float(p.get('venta_usd', 0))
                    v_bs = v_usd * tasa

                ganancia_usd = v_usd - c_usd
                ganancia_bs = v_bs - c_bs
                
                st.session_state.calc = {
                    "c_bs": c_bs, "c_usd": c_usd, 
                    "v_bs": v_bs, "v_usd": v_usd,
                    "g_bs": ganancia_bs, "g_usd": ganancia_usd
                }

        # --- MOSTRAR RESULTADOS Y GUARDAR ---
        if st.session_state.calc:
            c = st.session_state.calc
            st.markdown("### 📊 Resultado del Análisis")
            res_col1, res_col2 = st.columns(2)
            res_col1.metric("VENTA FINAL BS", f"{c['v_bs']:.2f} Bs")
            res_col1.metric("GANANCIA BS", f"{c['g_bs']:.2f} Bs")
            
            res_col2.metric("VENTA FINAL USD", f"{c['v_usd']:.2f} $")
            res_col2.metric("GANANCIA USD", f"{c['g_usd']:.2f} $")
            
            if st.button("💾 GUARDAR TODO EN SUPABASE"):
                datos = {
                    "codigo": cod_actual, "nombre": nombre.upper(),
                    "costo_bs": c['c_bs'], "costo_usd": c['c_usd'],
                    "margen": margen, "venta_usd": c['v_usd'], "venta_bs": c['v_bs']
                }
                if p: # Si existe, actualiza usando identifi
                    supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
                else: # Si no existe, inserta
                    supabase.table("productos").insert(datos).execute()
                
                st.success("✅ ¡Sincronizado con la nube!")
                st.session_state.calc = {}
