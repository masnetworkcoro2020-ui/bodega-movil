import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Royal Essence Móvil", layout="centered")
supabase = conectar()

if 'codigo_escaneado' not in st.session_state:
    st.session_state.codigo_escaneado = ""

st.title("🛒 Royal Essence - Bodega")

menu = ["📸 Escáner / Buscar", "📝 Editar o Agregar", "📦 Inventario Completo"]
opcion = st.sidebar.radio("Menú:", menu)

# --- MÉDULA 1: ESCÁNER ---
if opcion == "📸 Escáner / Buscar":
    st.subheader("Paso 1: Escanear para encontrar")
    foto = st.camera_input("Enfoca el producto")
    if foto:
        imagen = Image.open(foto)
        codigos = decode(imagen)
        if codigos:
            lectura = codigos[0].data.decode('utf-8').strip()
            st.session_state.codigo_escaneado = lectura[1:] if len(lectura) == 13 and lectura.startswith('0') else lectura
            st.success(f"✅ Detectado: {st.session_state.codigo_escaneado}")
            st.info("Pasa a 'Editar o Agregar' para modificar los datos.")
        else:
            st.warning("No se leyó nada.")

# --- MÉDULA 2: EDITAR O AGREGAR (LA NUEVA FUNCIÓN) ---
elif opcion == "📝 Editar o Agregar":
    st.subheader("Modificar Datos de Producto")
    cod_actual = st.text_input("Código de barras:", value=st.session_state.codigo_escaneado)
    
    if cod_actual:
        res = supabase.table("productos").select("*").eq("codigo", cod_actual).execute()
        
        # SI EL PRODUCTO EXISTE -> MODO EDICIÓN
        if res.data:
            p = res.data[0]
            st.warning(f"Editando: {p.get('nombre')}")
            
            with st.form("form_edicion"):
                nuevo_nombre = st.text_input("Nombre del producto", value=p.get('nombre'))
                nuevo_precio = st.number_input("Precio USD $", value=float(p.get('venta_usd', 0)), format="%.2f")
                # Si creaste la columna existencia, la editamos aquí
                nueva_existencia = st.number_input("Existencia / Stock", value=int(p.get('existencia', 0))) if 'existencia' in p else None
                
                if st.form_submit_button("✅ Guardar Cambios"):
                    datos_update = {
                        "nombre": nuevo_nombre.upper(),
                        "venta_usd": nuevo_precio
                    }
                    if nueva_existencia is not None:
                        datos_update["existencia"] = nueva_existencia
                    
                    # Usamos 'identifi' que es tu columna ID según la foto
                    supabase.table("productos").update(datos_update).eq("identifi", p['identifi']).execute()
                    st.success("¡Producto actualizado con éxito!")
                    st.balloons()
        
        # SI NO EXISTE -> MODO AGREGAR NUEVO
        else:
            st.info("Este código no está registrado. Puedes agregarlo ahora:")
            with st.form("form_nuevo"):
                nom_n = st.text_input("Nombre del Nuevo Producto")
                pre_n = st.number_input("Precio USD $", min_value=0.0, format="%.2f")
                if st.form_submit_button("➕ Registrar Producto Nuevo"):
                    supabase.table("productos").insert({
                        "codigo": cod_actual, "nombre": nom_n.upper(), "venta_usd": pre_n
                    }).execute()
                    st.success("¡Registrado!")

# --- MÉDULA 3: INVENTARIO ---
elif opcion == "📦 Inventario Completo":
    st.subheader("Lista de Productos")
    try:
        res = supabase.table("productos").select("codigo, nombre, venta_usd").execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
