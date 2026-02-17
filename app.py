import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from config import conectar

# Configuración
st.set_page_config(page_title="Lyan - Gestión 360", layout="centered")
supabase = conectar()

# --- LOGIN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.title("🔐 Acceso")
    u, c = st.text_input("Usuario"), st.text_input("Clave", type="password")
    if st.button("Entrar"):
        res = supabase.table("usuarios").select("*").eq("usuario", u).eq("clave", c).execute()
        if res.data: 
            st.session_state.autenticado = True
            st.session_state.user = res.data[0]['usuario']
            st.rerun()
    st.stop()

# --- DATOS DE SESIÓN ---
if 'codigo_escaneado' not in st.session_state: st.session_state.codigo_escaneado = ""

# Obtener Tasa
res_t = supabase.table("ajustes").select("valor").eq("id", 1).execute()
tasa = float(res_t.data[0]['valor']) if res_t.data else 40.0

st.title("📸 Escáner & Gestión 360°")
st.sidebar.metric("Tasa del Día", f"{tasa} Bs/$")

# 1. ESCÁNER (El Bolsillo)
foto = st.camera_input("Escanear Producto")
if foto:
    img = Image.open(foto)
    dets = decode(img)
    if dets:
        raw = dets[0].data.decode('utf-8').strip()
        st.session_state.codigo_escaneado = raw[1:] if len(raw)==13 and raw.startswith('0') else raw
        st.success(f"Código: {st.session_state.codigo_escaneado}")

# 2. FORMULARIO 360°
st.divider()
cod = st.text_input("Código de Producto", value=st.session_state.codigo_escaneado)

if cod:
    # Buscar si existe
    res_p = supabase.table("productos").select("*").eq("codigo", cod).execute()
    p = res_p.data[0] if res_p.data else {}
    
    with st.form("form_gestion"):
        nombre = st.text_input("Nombre del Producto", value=p.get('nombre', ''))
        margen = st.number_input("Ganancia %", value=float(p.get('margen', 25.0)))
        
        st.write("### Introduzca solo UN valor para calcular:")
        c1, c2 = st.columns(2)
        in_cbs = c1.number_input("Costo Bs", value=0.0, key="cbs")
        in_cusd = c2.number_input("Costo $", value=0.0, key="cusd")
        in_vbs = c1.number_input("Venta Bs", value=0.0, key="vbs")
        in_vusd = c2.number_input("Venta $", value=0.0, key="vusd")

        # --- LÓGICA 360° (Tus 4 condiciones) ---
        m_calc = margen / 100
        res_cbs, res_cusd, res_vbs, res_vusd = 0.0, 0.0, 0.0, 0.0

        if in_vbs > 0: # Condición 1: Venta Bs
            res_vbs = in_vbs; res_vusd = res_vbs / tasa
            res_cusd = res_vusd / (1 + m_calc); res_cbs = res_cusd * tasa
        elif in_vusd > 0: # Condición 2: Venta $
            res_vusd = in_vusd; res_vbs = res_vusd * tasa
            res_cusd = res_vusd / (1 + m_calc); res_cbs = res_cusd * tasa
        elif in_cbs > 0: # Condición 3: Costo Bs
            res_cbs = in_cbs; res_cusd = res_cbs / tasa
            res_vusd = res_cusd * (1 + m_calc); res_vbs = res_vusd * tasa
        elif in_cusd > 0: # Condición 4: Costo $
            res_cusd = in_cusd; res_cbs = res_cusd * tasa
            res_vusd = res_cusd * (1 + m_calc); res_vbs = res_vusd * tasa
        else: # Carga inicial si existe
            res_cusd = float(p.get('costo_usd', 0.0)); res_vusd = float(p.get('venta_usd', 0.0))
            res_cbs = res_cusd * tasa; res_vbs = res_vusd * tasa

        st.info(f"💡 RESULTADO: Costo: {res_cusd:.2f}$ ({res_cbs:.2f}Bs) | VENTA: {res_vusd:.2f}$ ({res_vbs:.2f}Bs)")

        if st.form_submit_button("💾 GUARDAR PRODUCTO"):
            datos = {
                "codigo": cod, "nombre": nombre.upper(), "margen": margen,
                "costo_bs": round(res_cbs, 2), "costo_usd": round(res_cusd, 2),
                "venta_bs": round(res_vbs, 2), "venta_usd": round(res_vusd, 2)
            }
            if p: supabase.table("productos").update(datos).eq("identifi", p['identifi']).execute()
            else: supabase.table("productos").insert(datos).execute()
            st.success("✅ ¡Guardado en la Nube!")
            st.session_state.codigo_escaneado = ""
            st.rerun()
