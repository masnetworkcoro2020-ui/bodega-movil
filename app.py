import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Móvil Pro", layout="centered")
supabase = conectar()

# --- FUNCIÓN PARA OBTENER TASA (Igual que en tu inventario.py) ---
def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa = obtener_tasa()

if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Gestión de Bodega Pro")
st.sidebar.info(f" Tasa actual: {tasa} Bs/$")

menu = ["📸 Escáner", "📝 Editar Producto", "📦 Inventario Completo"]
opcion = st.sidebar.radio("Ir a:", menu)

# --- ESCÁNER ---
if opcion == "📸 Escáner":
    st.subheader("Paso 1: Escanea el producto")
    foto = st.camera_input("Enfoca el código")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            lectura = codigos[0].data.decode('utf-8').strip()
            # Limpieza para códigos de 12 dígitos
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Código: {st.session_state.codigo_escaneado}")
            st.info("Ve a 'Editar Producto' para ver toda la información.")

# --- EDITAR PRODUCTO (CON TODOS LOS CAMPOS DE TU TABLA) ---
elif opcion == "📝 Editar Producto":
    st.subheader("Ficha Completa del Producto")
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        
        if res.data:
            p = res.data[0]
            with st.form("form_completo"):
                st.markdown(f"### 📋 {p.get('nombre')}")
                
                nombre = st.text_input("Nombre del Producto", value=p.get('nombre'))
                
                col1, col2 = st.columns(2)
                with col1:
                    c_usd = st.number_input("Costo USD $", value=float(p.get('costo_usd', 0)), format="%.2f")
                    v_usd = st.number_input("Venta USD $", value=float(p.get('venta_usd', 0)), format="%.2f")
                with col2:
                    margen = st.number_input("Margen %", value=float(p.get('margen', 25)))
                    v_bs = st.number_input("Venta Bs (Referencial)", value=float(v_usd * tasa), format="%.2f")
                
                # Campo de existencia (si ya creaste la columna)
                existencia = st.number_input("Existencia Actual", value=int(p.get('existencia', 0))) if 'existencia' in p else None

                if st.form_submit_button("💾 ACTUALIZAR TODO EN LA NUBE"):
                    datos = {
                        "nombre": nombre.upper(),
                        "costo_usd": c_usd,
                        "venta_usd": v_usd,
                        "margen": margen,
                        "venta_bs": v_bs,
                        "costo_bs": c_usd * tasa # Calculado automático
                    }
                    if existencia is not None: datos["existencia"] = existencia
                    
                    supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
                    st.success("✅ ¡Información actualizada!")
                    st.balloons()
        else:
            st.error("Producto no encontrado. Verifica el código.")

# --- INVENTARIO ---
elif opcion == "📦 Inventario Completo":
    st.subheader("Vista Global")
    res = supabase.table("productos").select("codigo, nombre, costo_usd, venta_usd, margen").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
