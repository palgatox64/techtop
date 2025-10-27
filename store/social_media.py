import facebook
import requests
from django.conf import settings
from .models import SocialMediaConfig, SocialMediaPost, Producto


class SocialMediaService:
    """Servicio para manejar publicaciones en redes sociales"""
    
    @staticmethod
    def format_message(template, producto):
        """Formatea el mensaje usando la plantilla y los datos del producto"""
        return template.format(
            nombre=producto.nombre,
            descripcion=producto.descripcion or '',
            precio=producto.precio,
            marca=producto.marca.nombre if producto.marca else '',
            categoria=producto.categoria.nombre if producto.categoria else ''
        )
    
    @staticmethod
    def publish_to_facebook(producto, config):
        """
        Publica un producto en Facebook.
        
        Args:
            producto: Instancia del modelo Producto
            config: Instancia del modelo SocialMediaConfig para Facebook
            
        Returns:
            dict: Resultado de la publicación con 'success', 'post_id' y 'message'
        """
        try:
            # Inicializar el SDK de Facebook
            graph = facebook.GraphAPI(access_token=config.access_token)
            
            # Formatear el mensaje
            message = SocialMediaService.format_message(config.template_message, producto)
            
            # Preparar datos para la publicación
            post_data = {
                'message': message,
            }
            
            # Si el producto tiene imagen, incluirla
            if producto.imagen:
                # Obtener URL completa de la imagen
                image_url = producto.imagen.url
                if not image_url.startswith('http'):
                    # Si es una URL relativa, convertirla a absoluta
                    from django.contrib.sites.models import Site
                    current_site = Site.objects.get_current()
                    image_url = f"https://{current_site.domain}{image_url}"
                
                post_data['link'] = image_url
            
            # Publicar en Facebook
            post = graph.put_object(
                parent_object=config.page_id,
                connection_name='feed',
                **post_data
            )
            
            return {
                'success': True,
                'post_id': post.get('id'),
                'message': message
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': message if 'message' in locals() else ''
            }
    
    @staticmethod
    def publish_to_instagram(producto, config):
        """
        Publica un producto en Instagram.
        
        Instagram requiere un proceso de dos pasos:
        1. Crear un contenedor de medios
        2. Publicar el contenedor
        
        Args:
            producto: Instancia del modelo Producto
            config: Instancia del modelo SocialMediaConfig para Instagram
            
        Returns:
            dict: Resultado de la publicación con 'success', 'post_id' y 'message'
        """
        try:
            # Formatear el mensaje (caption)
            caption = SocialMediaService.format_message(config.template_message, producto)
            
            # Verificar que el producto tenga imagen (requerido para Instagram)
            if not producto.imagen:
                return {
                    'success': False,
                    'error': 'Instagram requiere una imagen para publicar',
                    'message': caption
                }
            
            # Obtener URL completa de la imagen
            image_url = producto.imagen.url
            if not image_url.startswith('http'):
                from django.contrib.sites.models import Site
                current_site = Site.objects.get_current()
                image_url = f"https://{current_site.domain}{image_url}"
            
            # URL base de la API de Instagram
            base_url = f"https://graph.facebook.com/v18.0/{config.page_id}"
            
            # Paso 1: Crear contenedor de medios
            container_url = f"{base_url}/media"
            container_params = {
                'image_url': image_url,
                'caption': caption,
                'access_token': config.access_token
            }
            
            container_response = requests.post(container_url, params=container_params)
            container_data = container_response.json()
            
            if 'id' not in container_data:
                return {
                    'success': False,
                    'error': container_data.get('error', {}).get('message', 'Error creando contenedor'),
                    'message': caption
                }
            
            creation_id = container_data['id']
            
            # Paso 2: Publicar el contenedor
            publish_url = f"{base_url}/media_publish"
            publish_params = {
                'creation_id': creation_id,
                'access_token': config.access_token
            }
            
            publish_response = requests.post(publish_url, params=publish_params)
            publish_data = publish_response.json()
            
            if 'id' not in publish_data:
                return {
                    'success': False,
                    'error': publish_data.get('error', {}).get('message', 'Error publicando en Instagram'),
                    'message': caption
                }
            
            return {
                'success': True,
                'post_id': publish_data['id'],
                'message': caption
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': caption if 'caption' in locals() else ''
            }
    
    @staticmethod
    def publish_producto(producto_id):
        """
        Publica un producto en todas las redes sociales habilitadas.
        
        Args:
            producto_id: ID del producto a publicar
            
        Returns:
            list: Lista de resultados de cada publicación
        """
        try:
            producto = Producto.objects.get(pk=producto_id)
        except Producto.DoesNotExist:
            return [{'success': False, 'error': 'Producto no encontrado'}]
        
        results = []
        
        # Obtener configuraciones activas
        configs = SocialMediaConfig.objects.filter(enabled=True)
        
        for config in configs:
            # Publicar según la plataforma
            if config.platform == 'facebook':
                result = SocialMediaService.publish_to_facebook(producto, config)
            elif config.platform == 'instagram':
                result = SocialMediaService.publish_to_instagram(producto, config)
            else:
                result = {'success': False, 'error': f'Plataforma no soportada: {config.platform}'}
            
            # Registrar la publicación en la base de datos
            post = SocialMediaPost.objects.create(
                producto=producto,
                platform=config.platform,
                status='success' if result['success'] else 'failed',
                post_id=result.get('post_id', ''),
                message=result.get('message', ''),
                error_message=result.get('error', '')
            )
            
            results.append({
                'platform': config.platform,
                'success': result['success'],
                'post_id': result.get('post_id'),
                'error': result.get('error')
            })
        
        return results
