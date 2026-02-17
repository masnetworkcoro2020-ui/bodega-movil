import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence 360°", layout="centered")
supabase = conectar()

def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa = obtener_tasa()

if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🔄 Gestión 360° Móvil")
st.sidebar.metric("Tasa BCV", f"{tasa} Bs")

menu = ["📸 Escáner", "📝 Gestionar Producto", "📦 Inventario"]
opcion = st.sidebar.radio("Menú:", menu)

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
        else:
            st.warning("No se leyó nada.")

# --- GESTIÓN 360° (AGREGAR / EDITAR) ---
elif opcion == "📝 Gestionar Producto":
    st.subheader("Algoritmo de Precios 360°")
    cod_actual = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        p = res.data[0] if res.data else {}
        es_nuevo = len(p) == 0
        
        if not es_nuevo: st.warning(f"Editando: {p.get('nombre')}")
        else: st.info("✨ Registrando producto nuevo")

        # --- EL FORMULARIO CON BOTÓN DE ENVÍO ---
        with st.form("form_360_fijo"):
            nombre = st.text_input("Nombre del Producto", value=p.get('nombre', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                # Entrada de Costo Bs (Fijo como en tu PC)
                c_bs = st.number_input("Costo Bs", value=float(p.get('costo_bs', 0.0)), format="%.2f")
                # Cálculo de Costo USD basado en Tasa
                c_usd = c_bs / tasa if tasa > 0 else 0.0
                st.write(f"📉 Costo USD: ${c_usd:.2f}")
                
            with col2:
                # Margen de Ganancia
                margen = st.number_input("Margen %", value=float(p.get('margen', 25.0)), step=1.0)
            
            st.markdown("---")
            # CÁLCULO 360: Venta USD = Costo USD * (1 + Margen/100) según tu inventario.py
            v_usd_sugerida = c_usd * (1 + (margen/100))
            
            v_usd = st.number_input("Venta USD $", value=float(p.get('venta_usd', v_usd_sugerida)), format="%.2f")
            
            # Venta Bs final basada en Venta USD * Tasa
            v_bs = v_usd * tasa
            st.subheader(f"💰 Venta Final: {v_bs:.2f} Bs")
            
            # ¡ESTE ES EL BOTÓN QUE FALTABA!
            enviar = st.form_submit_button("🚀 GUARDAR CAMBIOS 360°")
            
            if enviar:
                if nombre:
                    datos = {
                        "codigo": cod_actual,
                        "nombre": nombre.upper(),
                        "costo_bs": c_bs,
                        "costo_usd": round(c_usd, 2),
                        "margen": margen,
                        "venta_usd": v_usd,
                        "venta_bs": round(v_bs, 2)
                    }
                    
                    if es_nuevo:
                        supabase.table("productos").insert(datos).execute()
                        st.success("✅ ¡Registrado con éxito!")
                    else:
                        # Usamos identifi que es tu ID original de la tabla
                        supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
                        st.success("✅ ¡Actualización 360 completada!")
                    st.session_state.codigo_escaneado = ""
                else:
                    st.error("Debes poner un nombre al producto.")

# --- INVENTARIO ---
elif opcion == "📦 Inventario":
    st.subheader("Lista Maestra")
    res = supabase.table("productos").select("codigo, nombre, venta_usd, venta_bs").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
