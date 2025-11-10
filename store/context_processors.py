from .models import Marca, Producto, Notificacion, Cliente

def menu_context(request):
    radio_brands = Marca.objects.filter(producto__categoria__nombre='RADIO ANDROID').distinct().order_by('nombre')
    featured_radios = Producto.objects.filter(categoria__nombre='RADIO ANDROID').order_by('-fecha_pub')[:4]
    
    cart = request.session.get('cart', {})
    cart_item_count = len(cart)
    
    is_empleado = request.session.get('user_type') == 'empleado'

    notificaciones_no_leidas = 0
    if request.session.get('user_type') == 'cliente':
         cliente_id = request.session.get('cliente_id')
         if cliente_id:
             notificaciones_no_leidas = Notificacion.objects.filter(
                 cliente_id=cliente_id, 
                 leida=False
             ).count()

    return {
        'radio_brands': radio_brands,
        'featured_radios': featured_radios,
        'cart_item_count': cart_item_count,
        'is_empleado': is_empleado,
        'notificaciones_count': notificaciones_no_leidas, 
    }