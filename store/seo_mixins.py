from meta.views import MetadataMixin
from django.conf import settings

class ProductSEOMixin(MetadataMixin):
    """Mixin para SEO de productos"""
    
    def get_meta_title(self, context=None):
        if hasattr(self, 'object') and self.object:
            return f"{self.object.nombre} - Techtop"
        return "Techtop - Tecnología y Electrónica"
    
    def get_meta_description(self, context=None):
        if hasattr(self, 'object') and self.object:
            desc = self.object.descripcion[:150] if self.object.descripcion else ''
            return f"{desc}... Compra en Techtop con envío a todo Chile."
        return "Tienda de tecnología, radios Android, electrónica automotriz y más. Envíos a todo Chile."
    
    def get_meta_image(self, context=None):
        if hasattr(self, 'object') and self.object and self.object.imagen:
            # Construir URL absoluta de la imagen
            if self.object.imagen.url.startswith('http'):
                return self.object.imagen.url
            return f"{settings.META_SITE_PROTOCOL}://{settings.META_SITE_DOMAIN}{self.object.imagen.url}"
        return f"{settings.META_SITE_PROTOCOL}://{settings.META_SITE_DOMAIN}/static/img/logo.png"
    
    def get_meta_keywords(self, context=None):
        keywords = ['techtop', 'comprar', 'chile']
        if hasattr(self, 'object') and self.object:
            if self.object.marca:
                keywords.append(self.object.marca.nombre.lower())
            if self.object.categoria:
                keywords.append(self.object.categoria.nombre.lower())
        return keywords


class CatalogSEOMixin(MetadataMixin):
    """Mixin para SEO de catálogos"""
    
    def get_meta_title(self, context=None):
        category = getattr(self, 'category_name', 'Productos')
        return f"{category} - Catálogo Techtop"
    
    def get_meta_description(self, context=None):
        category = getattr(self, 'category_name', 'productos')
        return f"Explora nuestro catálogo de {category}. Encuentra los mejores precios y envío a todo Chile. Compra seguro en Techtop."
    
    def get_meta_image(self, context=None):
        return f"{settings.META_SITE_PROTOCOL}://{settings.META_SITE_DOMAIN}/static/img/logo.png"