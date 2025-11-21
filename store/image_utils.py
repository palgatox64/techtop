from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def convert_to_webp(image_file, quality=85, max_width=1920, max_height=1920):
    """
    Convierte una imagen a formato WebP y la optimiza.
    
    Args:
        image_file: Archivo de imagen subido (UploadedFile)
        quality: Calidad de compresión WebP (1-100, default 85)
        max_width: Ancho máximo permitido
        max_height: Alto máximo permitido
    
    Returns:
        InMemoryUploadedFile: Archivo WebP optimizado listo para guardar
    """
    try:
        
        img = Image.open(image_file)
        
        
        if img.mode in ('RGBA', 'LA', 'P'):
            
            img = img.convert('RGBA')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        
        output = BytesIO()
        
        
        img.save(
            output,
            format='WEBP',
            quality=quality,
            method=6  
        )
        output.seek(0)
        
        
        original_name = image_file.name
        name_without_ext = original_name.rsplit('.', 1)[0]
        new_name = f"{name_without_ext}.webp"
        
        
        webp_file = InMemoryUploadedFile(
            output,
            'ImageField',
            new_name,
            'image/webp',
            sys.getsizeof(output),
            None
        )
        
        return webp_file
        
    except Exception as e:
        print(f"Error al convertir imagen a WebP: {e}")
        
        return image_file


def optimize_product_image(image_file):
    """
    Optimiza una imagen de producto principal.
    Tamaño recomendado: 1200x1200px para productos.
    """
    return convert_to_webp(image_file, quality=85, max_width=1200, max_height=1200)


def optimize_additional_image(image_file):
    """
    Optimiza imágenes adicionales de productos.
    Mismo tamaño que las principales para consistencia.
    """
    return convert_to_webp(image_file, quality=85, max_width=1200, max_height=1200)


def optimize_comprobante_image(image_file):
    """
    Optimiza imágenes de comprobantes de pago.
    Mayor calidad y tamaño para legibilidad.
    """
    return convert_to_webp(image_file, quality=90, max_width=2400, max_height=2400)