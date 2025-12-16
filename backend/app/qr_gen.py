"""
Generador de códigos QR
"""

import qrcode
import io
from typing import Optional
import base64


def generar_qr(datos: str, tamaño: int = 10) -> bytes:
    """
    Generar código QR a partir de datos
    
    Args:
        datos: Información a codificar en el QR
        tamaño: Tamaño de la caja del QR (default: 10)
    
    Returns:
        Imagen PNG del código QR en bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=tamaño,
        border=4,
    )
    qr.add_data(datos)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar en bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


def generar_qr_base64(datos: str, tamaño: int = 10) -> str:
    """
    Generar código QR codificado en base64
    
    Args:
        datos: Información a codificar en el QR
        tamaño: Tamaño de la caja del QR
    
    Returns:
        String base64 de la imagen PNG del código QR
    """
    img_bytes = generar_qr(datos, tamaño)
    return base64.b64encode(img_bytes).decode()
