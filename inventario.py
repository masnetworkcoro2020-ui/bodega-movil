import streamlit as st
from PIL import Image, ImageOps
import numpy as np

# Intentos de importación para procesamiento de imagen
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
    Recibe la foto de st.camera_input y devuelve el código de barras limpio.
    """
    if not foto or not pyzbar:
        return None

    # 1. Convertir a imagen de PIL y a escala de grises
    img = Image.open(foto)
    img_np = np.array(ImageOps.grayscale(img))
    
    # 2. Intento de decodificación estándar
    decoded = pyzbar.decode(img_np)
    
    # 3. Si falla, aplicar filtro de blanco y negro puro (Threshold)
    if not decoded and cv2 is not None:
        _, thr = cv2.threshold(img_np, 127, 255, cv2.THRESH_BINARY)
        decoded = pyzbar.decode(thr)
    
    if decoded:
        raw_code = str(decoded[0].data.decode('utf-8')).strip()
        
        # Regla de oro: Quitar el 0 inicial si es UPC-A (Largo > 10)
        if raw_code.startswith('0') and len(raw_code) > 10:
            return raw_code[1:]
        return raw_code
    
    return None
