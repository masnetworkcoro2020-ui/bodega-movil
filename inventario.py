import streamlit as st
from supabase import create_client
from camera_input_live import camera_input_live
from pyzbar import pyzbar
from PIL import Image

# 1. CONFIGURACIÓN E INYECCIÓN DE ESTILO (Colores de tu versión PC)
st.set_page_config(page_title="Bodega Móvil 360", layout="centered")

st.markdown("""
    <style>
    .stMetric { background-color: #2b2b2b; padding: 10px; border-radius: 10px; border: 1px solid #444; }
    [data-testid="stMetricValue"] { color: #d4efdf !important; } /* Verde claro como tu ent_vbs */
    </style>
    """, unsafe_allow_stdio=True)

# Credenciales Supabase
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Tu clave completa
supabase = create_client(URL, KEY)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'pagina' not in st.session_state: st.session_state.pagina = "login"

# --- PORTERO DE SEGURIDAD ---
if not st.session_state.auth:
    st.title("🔐 Acceso Administrativo")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR", use_container_width=True):
        if u == "jmaar" and p == "15311751":
            st.session_state.auth = True
            st.session_state.pagina = "panel"
            st.rerun()
    st.stop()

# --- LÓGICA DE NAVEGACIÓN ---
if st.session_state.pagina == "panel":
    st.title("🕹️ Panel de Control")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 INVENTARIO 360", use_container_width=True):
            st.session_state.pagina = "inventario"
            st.rerun()
    with col2:
        if st.button("🪙 AJUSTAR TASA", use_container_width=True):
            st.session_state.pagina = "tasa"
            st.rerun()

elif st.session_state.pagina == "inventario":
    st.title("📦 Inventario 360°")
    if st.button("⬅️ VOLVER"):
        st.session_state.pagina = "panel"
        st.rerun()

    # --- OBTENER TASA (Con paracaídas) ---
    try:
        res_tasa = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        tasa_db = float(res_tasa.data[0]['valor']) if res_tasa.data else 42.5
    except:
        tasa_db = 42.5
    
    tasa = st.number_input("Tasa de Cambio (Bs):", value=tasa_db, format="%.2f")

    # --- ESCÁNER ---
    st.subheader("📷 Escanear Producto")
    img_file = camera_input_live()
    codigo_detectado = ""
    
    if img_file:
        decoded = pyzbar.decode(Image.open(img_file))
        if decoded:
            codigo_detectado = decoded[0].data.decode('utf-8')
            st.toast(f"✅ Código detectado: {codigo_detectado}")

    cod = st.text_input("Código de barras:", value=codigo_detectado)

    if cod:
        # Búsqueda en tu tabla 'productos'
        res = supabase.table("productos").select("*").eq("codigo", cod).execute()
        
        if res.data:
            p = res.data[0]
            
            # --- FÓRMULA 360° (Idéntica a tu código original) ---
            # costo_usd -> margen -> venta_usd -> venta_bs
            c_usd = float(p.get('costo_usd', 0))
            margen = float(p.get('margen', 25))
            
            v_usd = c_usd * (1 + (margen/100))
            v_bs = v_usd * tasa
            
            # --- INTERFAZ VISUAL ---
            st.divider()
            st.markdown(f"### {p['nombre']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("VENTA BS (Móvil)", f"{v_bs:.2f}")
            with col_b:
                st.metric("VENTA USD", f"{v_usd:.2f} $")
            
            with st.expander("Ver detalles de Reposición"):
                st.write(f"**Costo Originario:** {c_usd:.2f} $")
                st.write(f"**Margen aplicado:** {margen}%")
                st.write(f"**Tasa aplicada:** {tasa} Bs/$")
                
                # Botón para actualizar el margen rápido desde el móvil
                nuevo_margen = st.slider("Ajustar Margen (%)", 0, 100, int(margen))
                if st.button("Actualizar Margen"):
                    supabase.table("productos").update({"margen": nuevo_margen}).eq("codigo", cod).execute()
                    st.success("Margen actualizado")
                    st.rerun()
        else:
            st.error("Producto no registrado.")

elif st.session_state.pagina == "tasa":
    st.title("🪙 Tasa BCV")
    if st.button("⬅️ VOLVER"):
        st.session_state.pagina = "panel"
        st.rerun()
    
    # Intenta leer la tasa actual
    try:
        res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
        actual = res.data[0]['valor'] if res.data else "42.5"
    except: actual = "42.5"
    
    st.metric("Tasa Actual", f"{actual} Bs.")
    nueva = st.text_input("Nueva Tasa:", value=str(actual))
    
    if st.button("GUARDAR TASA EN NUBE"):
        try:
            supabase.table("ajustes").upsert({"id": 1, "valor": nueva}).execute()
            st.success("Tasa guardada en Supabase")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: Crea la tabla 'ajustes' en Supabase primero.")
