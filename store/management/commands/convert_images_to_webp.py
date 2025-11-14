from django.core.management.base import BaseCommand
from store.models import Producto, ImagenProducto, ComprobanteTransferencia
from store.image_utils import optimize_product_image, optimize_additional_image, optimize_comprobante_image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class Command(BaseCommand):
    help = 'Convierte todas las imágenes existentes a formato WebP y elimina las originales'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando conversión de imágenes a WebP...')
        
        # Convertir imágenes principales de productos
        productos = Producto.objects.exclude(imagen='')
        total = productos.count()
        for i, producto in enumerate(productos, 1):
            try:
                if producto.imagen and not producto.imagen.name.endswith('.webp'):
                    self.stdout.write(f'[{i}/{total}] Convirtiendo: {producto.nombre}')
                    
                    # Guardar la ruta de la imagen original
                    old_image_path = producto.imagen.name
                    
                    # Convertir a WebP
                    imagen_optimizada = optimize_product_image(producto.imagen)
                    producto.imagen.save(
                        imagen_optimizada.name,
                        ContentFile(imagen_optimizada.read()),
                        save=False
                    )
                    producto.save()
                    
                    # Eliminar la imagen original
                    if default_storage.exists(old_image_path):
                        default_storage.delete(old_image_path)
                        self.stdout.write(f'  ✓ Eliminada imagen original: {old_image_path}')
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error con {producto.nombre}: {e}'))
        
        # Convertir imágenes adicionales
        imagenes_adicionales = ImagenProducto.objects.all()
        total_adicionales = imagenes_adicionales.count()
        for i, img in enumerate(imagenes_adicionales, 1):
            try:
                if img.imagen and not img.imagen.name.endswith('.webp'):
                    self.stdout.write(f'[{i}/{total_adicionales}] Convirtiendo imagen adicional')
                    
                    # Guardar la ruta de la imagen original
                    old_image_path = img.imagen.name
                    
                    # Convertir a WebP
                    imagen_optimizada = optimize_additional_image(img.imagen)
                    img.imagen.save(
                        imagen_optimizada.name,
                        ContentFile(imagen_optimizada.read()),
                        save=False
                    )
                    img.save()
                    
                    # Eliminar la imagen original
                    if default_storage.exists(old_image_path):
                        default_storage.delete(old_image_path)
                        self.stdout.write(f'  ✓ Eliminada imagen original: {old_image_path}')
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error con imagen adicional: {e}'))
        
        # Convertir comprobantes de transferencia
        comprobantes = ComprobanteTransferencia.objects.all()
        total_comprobantes = comprobantes.count()
        for i, comprobante in enumerate(comprobantes, 1):
            try:
                if comprobante.imagen and not comprobante.imagen.name.endswith('.webp'):
                    self.stdout.write(f'[{i}/{total_comprobantes}] Convirtiendo comprobante')
                    
                    # Guardar la ruta de la imagen original
                    old_image_path = comprobante.imagen.name
                    
                    # Convertir a WebP
                    imagen_optimizada = optimize_comprobante_image(comprobante.imagen)
                    comprobante.imagen.save(
                        imagen_optimizada.name,
                        ContentFile(imagen_optimizada.read()),
                        save=False
                    )
                    comprobante.save()
                    
                    # Eliminar la imagen original
                    if default_storage.exists(old_image_path):
                        default_storage.delete(old_image_path)
                        self.stdout.write(f'  ✓ Eliminada imagen original: {old_image_path}')
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error con comprobante: {e}'))
        
        self.stdout.write(self.style.SUCCESS('¡Conversión completada!'))
        self.stdout.write(self.style.SUCCESS(f'Total procesado: {total} productos, {total_adicionales} imágenes adicionales, {total_comprobantes} comprobantes'))
