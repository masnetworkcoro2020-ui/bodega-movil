import streamlit as st
from PIL import Image, ImageOps
import numpy as np

# Intentos de importación para que no se caiga si falta algo
try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

try:
    import cv2
except ImportError:
    cv2 = None

def procesar_escaneo(foto):
    """
    Recibe la foto de st.camera_input y devuelve el código de barras procesado.
    """
    if not foto or not pyzbar:
        return None

    # 1. Convertir a imagen de PIL y a escala de grises para mejor lectura
    img = Image.open(foto)
    img_np = np.array(ImageOps.grayscale(img))
    
    # 2. Primer intento: Lectura estándar
    decoded = pyzbar.decode(img_np)
    
    # 3. Segundo intento: Si falla, aplicamos blanco y negro puro (Thresholding)
    if not decoded and cv2 is not None:
        _, thr = cv2.threshold(img_np, 127, 255, cv2.THRESH_BINARY)
        decoded = pyzbar.decode(thr)
    
    if decoded:
        raw_code = str(decoded[0].data.decode('utf-8')).strip()
        
        # Lógica de corrección UPC-A: quitar 0 inicial si el código es largo
        if raw_code.startswith('0') and len(raw_code) > 10:
            return raw_code[1:]
        return raw_code
    
    return None
