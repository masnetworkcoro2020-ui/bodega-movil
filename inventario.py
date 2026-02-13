import streamlit as st
from camera_input_live import camera_input_live
from pyzbar.pyzbar import decode
from PIL import Image

st.subheader("📷 Escáner de Nueva Generación")
imagen = camera_input_live()

if imagen:
    img = Image.open(imagen)
    datos = decode(img)
    if datos:
        codigo_detectado = datos[0].data.decode('utf-8')
        st.success(f"Código detectado: {codigo_detectado}")
