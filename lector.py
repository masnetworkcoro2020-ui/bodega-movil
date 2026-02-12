import streamlit as st
from PIL import Image, ImageOps
import numpy as np

try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

try:
    import cv2
except ImportError:
    cv2 = None

def procesar_escaneo(foto):
    if not foto or not pyzbar:
        return None

    # 1. Convertir a formato OpenCV
    file_bytes = np.asarray(bytearray(foto.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    # 2. Convertir a Grises y mejorar contraste
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Intentar lectura 1: Imagen original en grises
    decoded = pyzbar.decode(gray)
    
    if not decoded:
        # Intentar lectura 2: Umbral adaptativo (Elimina sombras y reflejos)
        # Esto hace que las barras resalten muchísimo
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        decoded = pyzbar.decode(thresh)

    if not decoded:
        # Intentar lectura 3: Dilatación (Engrosa las barras si están muy finas)
        kernel = np.ones((3,3), np.uint8)
        dilated = cv2.dilate(gray, kernel, iterations=1)
        decoded = pyzbar.decode(dilated)

    if decoded:
        raw_code = str(decoded[0].data.decode('utf-8')).strip()
        # Regla de oro de tu programa original: quitar 0 inicial
        if raw_code.startswith('0') and len(raw_code) > 10:
            return raw_code[1:]
        return raw_code
    
    return None
