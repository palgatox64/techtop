from .models import Marca, Producto
from django.db.models import Count

def menu_context(request):
    radio_brands = Marca.objects.filter(producto__categoria__nombre='RADIO ANDROID').distinct().order_by('nombre')
    featured_radios = Producto.objects.filter(categoria__nombre='RADIO ANDROID').order_by('-fecha_pub')[:4]
    cart = request.session.get('cart', {})
    cart_item_count = len(cart) 

    return {
        'radio_brands': radio_brands,
        'featured_radios': featured_radios,
        'cart_item_count': cart_item_count, 
    }