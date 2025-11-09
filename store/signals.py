from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto
import requests
import logging
import threading

logger = logging.getLogger(__name__)

WEBHOOK_URL = "https://n8n.warevision.net/webhook/8ca172dc-caef-4519-8ee5-92efe48bef25"

def send_webhook_request(payload):
    """
    Función auxiliar para enviar la petición al webhook en un thread separado.
    """
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
        logger.info(f"Webhook notificado exitosamente para producto {payload['product_id']}")
        
    except requests.RequestException as e:
        logger.error(f"Error al notificar webhook para producto {payload['product_id']}: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al notificar webhook: {str(e)}")

@receiver(post_save, sender=Producto)
def notify_webhook_on_product_creation(sender, instance, created, **kwargs):
    """
    Envía notificación al webhook cuando se crea un nuevo producto.
    Solo se ejecuta en la creación, no en actualizaciones.
    """
    if created:  # Solo cuando se crea, no cuando se edita
        # Verificar si se debe publicar en redes sociales
        publicar_redes = getattr(instance, '_publicar_redes', False)
        
        if not publicar_redes:
            logger.info(f"Producto {instance.id} creado sin publicación en redes sociales")
            return
        
        # Construir la URL completa del producto
        product_url = f"http://localhost:8000/producto/{instance.id}"
        
        # Obtener la imagen principal
        imagen_principal = None
        if hasattr(instance, 'imagen') and instance.imagen:
            imagen_principal = instance.imagen.url
        
        # Preparar los datos para enviar
        payload = {
            'product_id': instance.id,
            'product_name': instance.nombre,
            'product_url': product_url,
            'image_url': imagen_principal,
            'price': str(instance.precio) if hasattr(instance, 'precio') else None,
            'description': instance.descripcion if hasattr(instance, 'descripcion') else None,
        }
        
        # Enviar la petición en un thread separado para no bloquear la creación
        thread = threading.Thread(target=send_webhook_request, args=(payload,))
        thread.daemon = True
        thread.start()