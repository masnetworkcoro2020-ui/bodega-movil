import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Móvil Pro", layout="centered")
supabase = conectar()

# --- FUNCIÓN PARA OBTENER TASA (Igual a tu inventario.py) ---
def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa_actual = obtener_tasa()

if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Royal Essence - Gestión")
st.sidebar.metric("Tasa BCV", f"{tasa_actual} Bs")

menu = ["📸 Escáner", "📝 Editar Producto", "📦 Ver Inventario"]
opcion = st.sidebar.radio("Ir a:", menu)

# --- 1. ESCÁNER ---
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
            st.success(f"✅ Código capturado: {st.session_state.codigo_escaneado}")
            st.info("Ahora entra en 'Editar Producto'.")

# --- 2. EDITAR PRODUCTO (TODOS LOS CAMPOS) ---
elif opcion == "📝 Editar Producto":
    st.subheader("Ficha Técnica del Producto")
    cod_actual = st.text_input("Código:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        
        if res.data:
            p = res.data[0]
            with st.form("form_ajustes"):
                st.info(f"Editando: {p.get('nombre')}")
                
                nombre = st.text_input("Nombre", value=p.get('nombre'))
                
                # --- COSTOS ---
                col1, col2 = st.columns(2)
                with col1:
                    c_bs = st.number_input("Costo Bs (Fijo)", value=float(p.get('costo_bs', 0)), format="%.2f")
                    c_usd = st.number_input("Costo USD $", value=float(p.get('costo_usd', 0)), format="%.2f")
                with col2:
                    margen = st.number_input("Margen %", value=float(p.get('margen', 25)), step=1.0)
                    
                # --- VENTAS ---
                st.markdown("---")
                v_usd = st.number_input("Venta USD $", value=float(p.get('venta_usd', 0)), format="%.2f")
                # Venta Bs se calcula automático para mostrarte cómo queda con la tasa actual
                v_bs_movil = v_usd * tasa_actual
                st.write(f"**Venta Bs (Móvil):** {v_bs_movil:.2f} Bs")

                if st.form_submit_button("💾 GUARDAR CAMBIOS"):
                    datos = {
                        "nombre": nombre.upper(),
                        "costo_bs": c_bs,
                        "costo_usd": c_usd,
                        "margen": margen,
                        "venta_usd": v_usd,
                        "venta_bs": v_bs_movil # Se guarda la venta en Bs actualizada
                    }
                    # Usamos 'identifi' porque es tu ID en Supabase
                    supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
                    st.success("✅ ¡Base de datos actualizada!")
        else:
            st.error("Producto no encontrado.")

# --- 3. INVENTARIO ---
elif opcion == "📦 Ver Inventario":
    st.subheader("Existencias")
    res = supabase.table("productos").select("codigo, nombre, costo_bs, venta_usd").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
