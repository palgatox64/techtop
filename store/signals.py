from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto, Pedido, MensajeContacto, PagoTransferencia
import requests
import logging
import threading
import os
from django.utils import timezone

logger = logging.getLogger(__name__)

WEBHOOK_URL_PRODUCTOS = os.getenv(
    'WEBHOOK_URL_PRODUCTOS',
)

WEBHOOK_URL_COMPRAS = os.getenv(
    'WEBHOOK_URL_COMPRAS',
)

WEBHOOK_URL_CONTACTO = os.getenv(
    'WEBHOOK_URL_CONTACTO',
)

def send_webhook_request(payload, webhook_url):
    """
    Función auxiliar para enviar la petición al webhook en un thread separado.
    """
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
        logger.info(f"Webhook notificado exitosamente: {webhook_url}")
        
    except requests.RequestException as e:
        logger.error(f"Error al notificar webhook {webhook_url}: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al notificar webhook: {str(e)}")


@receiver(post_save, sender=Producto)
def notify_webhook_on_product_creation(sender, instance, created, **kwargs):
    """
    Envía notificación al webhook cuando se crea un nuevo producto.
    Solo se ejecuta en la creación, no en actualizaciones.
    """
    if created:
        publicar_redes = getattr(instance, '_publicar_redes', False)
        
        if not publicar_redes:
            logger.info(f"Producto {instance.id} creado sin publicación en redes sociales")
            return
        
        product_url = f"http://localhost:8000/producto/{instance.id}"
        
        imagen_principal = None
        if hasattr(instance, 'imagen') and instance.imagen:
            imagen_principal = instance.imagen.url
        
        payload = {
            'product_id': instance.id,
            'product_name': instance.nombre,
            'product_url': product_url,
            'image_url': imagen_principal,
            'price': str(instance.precio) if hasattr(instance, 'precio') else None,
            'description': instance.descripcion if hasattr(instance, 'descripcion') else None,
        }
        
        thread = threading.Thread(target=send_webhook_request, args=(payload, WEBHOOK_URL_PRODUCTOS))
        thread.daemon = True
        thread.start()


@receiver(post_save, sender=MensajeContacto)
def notify_webhook_on_contact_message(sender, instance, created, **kwargs):
    """
    Envía notificación al webhook cuando se guarda un nuevo mensaje de contacto.
    """
    if created:
        logger.info(f"Nuevo mensaje de contacto recibido de {instance.email}")
        
        # Convertir fecha a hora local de Chile (usando timezone.localtime)
        fecha_local = timezone.localtime(instance.fecha)
        
        payload = {
            "tipo": "Nuevo Mensaje de Contacto",
            "id_mensaje": instance.id,
            "nombre": instance.nombre,
            "apellido": instance.apellido,
            "email": instance.email,
            "mensaje": instance.mensaje,
            "fecha": fecha_local.strftime("%d/%m/%Y %H:%M:%S")
        }
        
        thread = threading.Thread(
            target=send_webhook_request, 
            args=(payload, WEBHOOK_URL_CONTACTO)
        )
        thread.daemon = True
        thread.start()


def enviar_notificacion_compra_webhook(pedido):
    """
    Función auxiliar para preparar y enviar la notificación de compra al webhook.
    Esta función puede ser llamada desde signals o directamente desde views.
    """
    try:
        # Obtener los detalles del pedido
        detalles = pedido.detalles.select_related('producto').all()
        
        # Información del cliente
        cliente_info = {
            'nombre_completo': 'Cliente no registrado',
            'email': 'No disponible',
            'rut': 'No disponible',
            'telefono': 'No disponible'
        }
        
        if pedido.cliente:
            cliente_info = {
                'nombre_completo': f"{pedido.cliente.nombre} {pedido.cliente.apellidos}",
                'email': pedido.cliente.email,
                'rut': getattr(pedido.cliente, 'rut', 'No disponible'),
                'telefono': pedido.cliente.telefono or 'No disponible'
            }
        
        # Información de la dirección de envío
        direccion_info = None
        if pedido.direccion_envio:
            direccion_info = {
                'calle': pedido.direccion_envio.calle,
                'numero': pedido.direccion_envio.numero,
                'ciudad': pedido.direccion_envio.ciudad,
                'region': pedido.direccion_envio.region,
                'codigo_postal': pedido.direccion_envio.codigo_postal or 'No especificado'
            }
        
        # Construir lista de productos
        productos_list = []
        for detalle in detalles:
            productos_list.append({
                'nombre': detalle.producto.nombre,
                'cantidad': detalle.cantidad,
                'precio_unitario': str(detalle.precio_unitario),
                'subtotal': str(detalle.precio_unitario * detalle.cantidad)
            })
        
        # Convertir fecha a hora local de Chile (usando timezone.localtime)
        fecha_pedido_local = timezone.localtime(pedido.fecha_pedido)
        
        # Preparar payload para el webhook
        payload = {
            'pedido_id': pedido.id,
            'tracking_number': pedido.tracking_number,
            'fecha_pedido': fecha_pedido_local.strftime("%d/%m/%Y %H:%M:%S"),  # Formato legible en hora local
            'total': str(pedido.total),
            'estado': pedido.estado,
            'metodo_pago': pedido.get_metodo_pago_display(),
            'tipo_entrega': 'Despacho a Domicilio' if pedido.direccion_envio else 'Retiro en Tienda',
            'cliente': cliente_info,
            'direccion_envio': direccion_info,
            'productos': productos_list,
            'cantidad_productos': len(productos_list),
            'url_detalle_pedido': f"http://localhost:8000/gestion/pedidos/{pedido.id}/"
        }
        
        # Enviar notificación al webhook en un thread separado
        logger.info(f"Enviando notificación de compra exitosa para pedido {pedido.id}")
        thread = threading.Thread(target=send_webhook_request, args=(payload, WEBHOOK_URL_COMPRAS))
        thread.daemon = True
        thread.start()
        
        return True
        
    except Exception as e:
        logger.error(f"Error al preparar notificación de compra para pedido {pedido.id}: {str(e)}")
        return False


@receiver(post_save, sender=Pedido)
def notify_webhook_on_successful_purchase(sender, instance, created, update_fields, **kwargs):
    """
    Envía notificación al webhook cuando un pedido cambia a estado 'procesando'.
    Solo notifica para pagos con Webpay y Mercado Pago (las transferencias se notifican desde la vista).
    """
    # Solo procesar si NO es una creación y el pedido cambió a 'procesando'
    if created:
        return
    
    # Verificar si el pedido acaba de cambiar a 'procesando'
    if instance.estado != 'procesando':
        return
    
    # Solo notificar para Webpay y Mercado Pago (las transferencias se manejan en la vista)
    if instance.metodo_pago not in ['webpay', 'mercadopago']:
        logger.info(f"Pedido {instance.id} con método {instance.metodo_pago} - no se notifica automáticamente")
        return
    
    # Verificar si ya se notificó anteriormente (para evitar duplicados)
    if hasattr(instance, '_webhook_notificado') and instance._webhook_notificado:
        return
    
    # Usar la función auxiliar para enviar la notificación
    if enviar_notificacion_compra_webhook(instance):
        # Marcar como notificado para evitar duplicados
        instance._webhook_notificado = True


@receiver(post_save, sender=PagoTransferencia)
def notify_webhook_on_transfer_approval(sender, instance, created, **kwargs):
    """
    Envía notificación al webhook cuando una transferencia es APROBADA.
    """
    # Solo notificar si NO es una creación y el estado cambió a APROBADO
    if created:
        return
    
    # Solo procesar si el estado es APROBADO
    if instance.estado != 'APROBADO':
        return
    
    # Verificar si ya se notificó (para evitar duplicados si se guarda múltiples veces)
    if hasattr(instance, '_webhook_notificado') and instance._webhook_notificado:
        return
    
    logger.info(f"Transferencia aprobada para pedido {instance.pedido.id}, notificando webhook...")
    
    # Usar la función auxiliar para enviar la notificación
    if enviar_notificacion_compra_webhook(instance.pedido):
        # Marcar como notificado
        instance._webhook_notificado = True

