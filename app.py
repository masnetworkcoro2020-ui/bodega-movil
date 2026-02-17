import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Móvil Pro", layout="centered")
supabase = conectar()

# --- FUNCIÓN TASA (Sincronizada con tu ajustes ID:1) ---
def obtener_tasa():
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        return float(res.data[0]['valor']) if res.data else 40.0
    except: return 40.0

tasa_actual = obtener_tasa()

if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Gestión de Bodega Pro")
st.sidebar.metric("Tasa de Cambio", f"{tasa_actual} Bs/$")

menu = ["📸 Escáner", "📝 Gestionar Producto", "📦 Inventario Completo"]
opcion = st.sidebar.radio("Menú:", menu)

# --- 1. ESCÁNER ---
if opcion == "📸 Escáner":
    st.subheader("Escaneo de Producto")
    foto = st.camera_input("Enfoca el código de barras")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            lectura = codigos[0].data.decode('utf-8').strip()
            # Limpieza exacta de ceros iniciales para UPC-A
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Código: {st.session_state.codigo_escaneado}")
            st.info("Pasa a 'Gestionar Producto' para continuar.")

# --- 2. GESTIONAR (EDITAR O AGREGAR NUEVO) ---
elif opcion == "📝 Gestionar Producto":
    st.subheader("Ficha de Producto")
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        
        # MODO EDICIÓN (Si ya existe)
        if res.data:
            p = res.data[0]
            st.warning(f"Modificando: {p.get('nombre')}")
            titulo_boton = "💾 GUARDAR CAMBIOS"
            modo_nuevo = False
        # MODO AGREGAR (Si es nuevo)
        else:
            st.info("✨ Producto Nuevo detectado. Completa los datos:")
            p = {} # Diccionario vacío para el formulario
            titulo_boton = "➕ REGISTRAR PRODUCTO"
            modo_nuevo = True

        with st.form("formulario_producto"):
            nombre = st.text_input("Nombre del Producto", value=p.get('nombre', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                c_bs = st.number_input("Costo Bs (Fijo)", value=float(p.get('costo_bs', 0)), format="%.2f")
                c_usd = st.number_input("Costo USD $", value=float(p.get('costo_usd', 0)), format="%.2f")
            with col2:
                margen = st.number_input("Margen %", value=float(p.get('margen', 25)), step=1.0)
                v_usd = st.number_input("Venta USD $", value=float(p.get('venta_usd', 0)), format="%.2f")
            
            # Cálculo informativo en tiempo real
            v_bs_estimada = v_usd * tasa_actual
            st.write(f"💡 **Venta estimada en Bs:** {v_bs_estimada:.2f}")

            if st.form_submit_button(titulo_boton):
                if nombre:
                    datos = {
                        "codigo": cod_actual,
                        "nombre": nombre.upper(),
                        "costo_bs": c_bs,
                        "costo_usd": c_usd,
                        "margen": margen,
                        "venta_usd": v_usd,
                        "venta_bs": v_bs_estimada
                    }
                    
                    if modo_nuevo:
                        supabase.table("productos").insert(datos).execute()
                        st.success("✅ Producto registrado exitosamente.")
                    else:
                        supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
                        st.success("✅ Datos actualizados correctamente.")
                    
                    st.session_state.codigo_escaneado = "" # Limpiar para el siguiente
                else:
                    st.error("El nombre es obligatorio.")

# --- 3. INVENTARIO ---
elif opcion == "📦 Inventario Completo":
    st.subheader("Resumen de Almacén")
    res = supabase.table("productos").select("codigo, nombre, venta_usd").order("nombre").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
