# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.db.models import Count, Q
from django.db import IntegrityError, transaction
from django.core.validators import validate_email
from django.core.mail import send_mail, EmailMessage
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.urls import reverse
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.utils import timezone
import datetime
from .forms import ComprobantePagoForm, PerfilUsuarioForm, ComentarioForm, CheckoutForm
from .models import Notificacion, PagoTransferencia, ComprobanteTransferencia
from django.db.models import Sum, Count, F, Q, Case, When, Value, IntegerField, Avg
from decimal import Decimal
from io import BytesIO
from xhtml2pdf import pisa
import re
import csv
import json
import unicodedata 
import random      
from django.db.models import Q
import unicodedata
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Local imports
from .models import Producto, Marca, Categoria, Cliente, Empleado, Pedido, DetallePedido, Direccion, TransaccionWebpay, TransaccionMercadoPago, Comentario, PasswordResetToken
from .decorators import admin_required, superadmin_required
from .forms import CategoriaForm, MarcaForm, ProductoForm, CheckoutForm, EmpleadoForm
from .validators import validate_chilean_rut
from .models import MensajeContacto
# --- VISTAS PARA GESTIÓN DE EMPLEADOS (SOLO SUPERADMIN) ---

@superadmin_required
def gestion_empleados(request):
    """
    Lista todos los empleados para que el superadmin los gestione.
    """
    empleados_list = Empleado.objects.all().order_by('apellidos', 'nombre')
    
    paginator = Paginator(empleados_list, 10) # 10 empleados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gestion/empleados_list.html', {'page_obj': page_obj})

@superadmin_required
def crear_empleado(request):
    """
    Muestra el formulario para crear un nuevo empleado y procesa su creación.
    """
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save() # El método save del form ya hashea la contraseña
            messages.success(request, '¡Empleado creado exitosamente!', extra_tags='swal-success')
            return redirect('gestion_empleados')
    else:
        form = EmpleadoForm()
    
    return render(request, 'gestion/crear_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo Empleado'
    })

@superadmin_required
def editar_empleado(request, pk):
    """
    Muestra el formulario para editar un empleado existente y procesa los cambios.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Empleado "{empleado.nombre} {empleado.apellidos}" actualizado exitosamente!', extra_tags='swal-success')
            return redirect('gestion_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    
    return render(request, 'gestion/editar_form.html', {
        'form': form,
        'titulo': f'Editar Empleado: {empleado.nombre} {empleado.apellidos}',
        'objeto_id': empleado.pk,
        'volver_url': 'gestion_empleados'
    })

@superadmin_required
@require_http_methods(["POST"])
def eliminar_empleado(request, pk):
    """
    Desactiva la cuenta de un empleado en lugar de eliminarla.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    
    # Evitar que un superadmin se desactive a sí mismo
    if empleado.id_empleado == request.session.get('empleado_id'):
        return JsonResponse({'success': False, 'message': 'No puedes desactivar tu propia cuenta.'}, status=403)

    empleado.activo = False
    empleado.save()
    
    return JsonResponse({'success': True, 'message': f'Empleado "{empleado.nombre} {empleado.apellidos}" ha sido desactivado.'})


def home(request):
    """Página de inicio con SEO optimizado"""
    from meta.views import Meta
    
    meta = Meta(
        title="Techtop - Radios Android, Electrónica Automotriz y Tecnología",
        description="Tienda líder en radios Android, electrónica automotriz y tecnología en Chile. Envío rápido a todo el país. ¡Encuentra los mejores precios y ofertas!",
        url=request.build_absolute_uri(),
        keywords=['techtop', 'radios android', 'electrónica automotriz', 'tecnología', 'chile', 'tienda online'],
        object_type='website'
    )
    
    context = {'meta': meta}
    return render(request, 'home.html', context)

def contacto(request):
    """Página de contacto con SEO"""
    from meta.views import Meta
    
    meta = Meta(
        title="Contacto - Techtop | Atención al Cliente",
        description="Contáctanos por WhatsApp, email o teléfono. Atención personalizada de lunes a viernes. Resolvemos todas tus dudas sobre productos y envíos.",
        url=request.build_absolute_uri(),
        keywords=['contacto techtop', 'atención cliente', 'whatsapp', 'soporte'],
        object_type='website'
    )
    
    context = {'meta': meta}
    return render(request, 'contacto.html', context)

def about(request):
    """Página Quiénes Somos con SEO"""
    from meta.views import Meta
    
    meta = Meta(
        title="Quiénes Somos - Techtop | Expertos en Tecnología Automotriz",
        description="Conoce la historia de Techtop, tu tienda de confianza en radios Android y tecnología automotriz en Chile. Más de 5 años mejorando tu experiencia de conducción.",
        url=request.build_absolute_uri(),
        keywords=['techtop', 'quienes somos', 'historia', 'empresa', 'tecnología automotriz'],
        object_type='website'
    )
    
    context = {'meta': meta}
    return render(request, 'about.html', context)

def seguimiento_compra(request):
    return render(request, 'seguimiento_compra.html')

def centro_ayuda(request):
    return render(request, 'centro_ayuda.html')

def garantias(request):
    """Página de garantías con SEO"""
    from meta.views import Meta
    
    meta = Meta(
        title="Garantías y Devoluciones - Techtop | Compra Segura",
        description="Conoce nuestras políticas de garantía, devoluciones y cambios. 6 meses de garantía legal en todos los productos. Compra con confianza en Techtop.",
        url=request.build_absolute_uri(),
        keywords=['garantías techtop', 'devoluciones', 'cambios', 'política', 'compra segura'],
        object_type='website'
    )
    
    context = {'meta': meta}
    return render(request, 'garantias.html', context)

def politicas_privacidad(request):
    return render(request, 'politicas_privacidad.html')

def terminos_condiciones(request):
    return render(request, 'terminos_condiciones.html')

def radios_catalog(request):
    products = Producto.objects.filter(categoria__nombre='RADIO ANDROID', activo=True)
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')
    selected_inches = request.GET.getlist('pulgadas')
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)
    if selected_inches:
        for inch_size in selected_inches:
            products = products.filter(nombre__icontains=inch_size)
    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)
    available_inches = ['7', '9', '10.1', '12']
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')
    # SEO para catálogo de radios
    from meta.views import Meta
    
    meta = Meta(
        title="Radios Android para Auto - Catálogo Completo | Techtop",
        description="Amplio catálogo de radios Android de 7, 9, 10.1 y 12 pulgadas. GPS, Bluetooth, WiFi y más. Instalación incluida. Envío a todo Chile.",
        url=request.build_absolute_uri(),
        keywords=['radios android', 'radio auto', 'gps', 'bluetooth', 'pantalla táctil', 'chile'],
        object_type='website'
    )
    
    context = {
        'products': products,
        'available_brands': available_brands,
        'available_inches': available_inches,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'selected_inches_from_form': selected_inches,
        'meta': meta,
    }
    
    return render(request, 'store/tienda.html', context)

def category_catalog(request, categoria_nombre):
    nombre_categoria_con_espacios = categoria_nombre.replace('-', ' ')
    categoria = get_object_or_404(Categoria, nombre__iexact=nombre_categoria_con_espacios)
    products = Producto.objects.filter(categoria=categoria)
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')
    category_type = 'subcategoria'
    if categoria_nombre in ['Audio-y-Video', 'Seguridad-y-Sensores', 'Diagnostico-Automotriz']:
        parent_category = 'accesorios'
    elif categoria_nombre in ['Electronica-Automotriz', 'Electronica-General']:
        parent_category = 'electronica'
    else:
        parent_category = None

    # SEO para la categoría
    meta = Meta(
        title=f"{categoria.nombre} - Catálogo Techtop",
        description=f"Descubre nuestra selección de {categoria.nombre.lower()} en Techtop. Encuentra los mejores productos con envío a todo Chile.",
        keywords=[categoria.nombre.lower(), 'techtop', 'chile', 'tecnología', 'comprar'],
        url=request.build_absolute_uri(),
        object_type='website'
    )

    context = {
        'products': products,
        'categoria_actual': categoria,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': category_type,
        'parent_category': parent_category,
        'meta': meta
    }
    
    return render(request, 'store/tienda.html', context)


def electronica_catalog(request):
    electronics_categories = [
        'Electronica Automotriz',
        'Electronica General',
        'Electronica',
    ]
    products = Producto.objects.filter(categoria__nombre__in=electronics_categories, activo=True)
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')
    selected_categories = request.GET.getlist('categoria')
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)
    
    if selected_categories:
        products = products.filter(categoria__nombre__in=selected_categories)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')

    available_categories = Categoria.objects.filter(
        nombre__in=electronics_categories,
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')


    # SEO para catálogo de electrónica
    from meta.views import Meta
    
    meta = Meta(
        title="Electrónica Automotriz - Catálogo Completo | Techtop",
        description="Productos de electrónica automotriz de alta calidad. Encuentra todo para equipar tu vehículo: sensores, cámaras, alarmas y más. Envío a todo Chile.",
        url=request.build_absolute_uri(),
        keywords=['electrónica automotriz', 'accesorios auto', 'sensores', 'cámaras', 'alarmas'],
        object_type='website'
    )
    
    context = {
        'products': products,
        'available_brands': available_brands,
        'available_categories': available_categories,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'selected_categories_from_form': selected_categories,
        'category_type': 'electronica',
        'meta': meta,
    }
    
    return render(request, 'store/tienda.html', context)

    
def accesorios_catalog(request):
    accessory_categories = [
        'Audio', 
        'Seguridad-y-Sensores', 
        'Diagnostico-Automotriz',
        'Herramientas-de-Medicion',
        'Medidores',
        'Parlante',     
        'Scanner',
        'Compresor',
        'Cargador'
    ]
    products = Producto.objects.filter(categoria__nombre__in=accessory_categories, activo=True)
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')
    selected_categories = request.GET.getlist('categoria')
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_categories:
        products = products.filter(categoria__nombre__in=selected_categories)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')

    available_categories = Categoria.objects.filter(
        nombre__in=accessory_categories,
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')


    # SEO para catálogo de accesorios
    from meta.views import Meta
    
    meta = Meta(
        title="Accesorios Automotrices - Audio, Seguridad y Diagnóstico | Techtop",
        description="Accesorios de calidad para tu vehículo: audio, parlantes, herramientas de diagnóstico, sensores de seguridad y más. Precios competitivos y envío rápido.",
        url=request.build_absolute_uri(),
        keywords=['accesorios auto', 'audio', 'parlantes', 'seguridad', 'diagnóstico', 'scanner'],
        object_type='website'
    )
    
    context = {
        'products': products,
        'available_brands': available_brands,
        'available_categories': available_categories,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'selected_categories_from_form': selected_categories,
        'category_type': 'accesorios',
        'meta': meta,
    }

    return render(request, 'store/tienda.html', context)

def otros_catalog(request):
    excluded_categories = [
        'RADIO ANDROID',
        'Electronica Automotriz',
        'Electronica General',
        'Electronica',
        'Audio', 
        'Seguridad-y-Sensores', 
        'Diagnostico-Automotriz',
        'Herramientas-de-Medicion',
        'Medidores',
        'Parlante',     
        'Scanner',
        'Compresor',
        'Cargador'
    ]
    
   
    products = Producto.objects.exclude(categoria__nombre__in=excluded_categories).filter(activo=True)
    
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')

    # SEO para otros productos
    meta = Meta(
        title="Otros Productos - Catálogo Techtop",
        description="Explora nuestra variedad de productos tecnológicos: herramientas, medidores, compresores y más. Encuentra lo que necesitas en Techtop.",
        keywords=['productos tecnológicos', 'herramientas', 'techtop', 'chile', 'comprar online'],
        url=request.build_absolute_uri(),
        object_type='website'
    )

    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'otros',
        'meta': meta
    }

    return render(request, 'store/tienda.html', context)

def product_catalog(request, brand_name=None):
    products = Producto.objects.filter(activo=True)
    if brand_name:
        products = products.filter(marca__nombre__iexact=brand_name)

    selected_brands = request.GET.getlist('marca')
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    available_brands = Marca.objects.annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre') 

    # SEO para catálogo de productos (general o por marca)
    if brand_name:
        meta = Meta(
            title=f"Productos {brand_name} - Techtop",
            description=f"Descubre todos los productos de la marca {brand_name} disponibles en Techtop. Calidad garantizada y envío a todo Chile.",
            keywords=[brand_name.lower(), 'productos', 'techtop', 'chile', 'tecnología'],
            url=request.build_absolute_uri(),
            object_type='website'
        )
    else:
        meta = Meta(
            title="Catálogo de Productos - Techtop",
            description="Explora nuestro catálogo completo de productos tecnológicos. Encuentra radios Android, electrónica automotriz, accesorios y más en Techtop.",
            keywords=['catálogo', 'productos', 'techtop', 'tecnología', 'chile', 'comprar'],
            url=request.build_absolute_uri(),
            object_type='website'
        )
    
    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brand': brand_name,
        'selected_brands_from_form': selected_brands,
        'meta': meta
    }
    return render(request, 'store/tienda.html', context)


def get_cart_data(request):
    cart = request.session.get('cart', {})
    cart_items_data = []
    total_price = Decimal('0.00')

    if cart:
        product_ids = cart.keys()
        products_in_cart = Producto.objects.filter(id__in=product_ids)

        for p in products_in_cart:
            pid_str = str(p.id)
            if pid_str in cart:
                qty = cart[pid_str]['quantity']
                precio_actual = p.precio_oferta
                
                total_price += precio_actual * qty
                
                cart_items_data.append({
                    'id': p.id,
                    'name': p.nombre,
                    'quantity': qty,
                    'price': float(precio_actual), 
                    'image_url': p.imagen.url if p.imagen and hasattr(p.imagen, 'url') else ''
                })

    return JsonResponse({
        'success': True,
        'cart_item_count': len(cart),
        'items': cart_items_data,
        'subtotal': float(total_price)
    })

def product_detail(request, product_id):
    """Vista de detalle de producto con SEO mejorado"""
    product = get_object_or_404(Producto, id=product_id)
    from meta.views import Meta
    
    # Construir URL absoluta de la imagen
    image_url = None
    if product.imagen:
        if product.imagen.url.startswith('http'):
            image_url = product.imagen.url
        else:
            image_url = request.build_absolute_uri(product.imagen.url)
    
    # Keywords dinámicos del producto
    keywords = ['techtop', 'comprar', 'chile']
    if product.marca:
        keywords.append(product.marca.nombre.lower())
    if product.categoria:
        keywords.append(product.categoria.nombre.lower())
    keywords.append(product.nombre.lower())
    
    # Configurar metadata SEO
    meta = Meta(
        title=f"{product.nombre} - Techtop",
        description=product.descripcion[:160] if product.descripcion else f"Compra {product.nombre} en Techtop. Envío a todo Chile.",
        image=image_url,
        url=request.build_absolute_uri(),
        object_type='product',
        keywords=keywords,
        extra_custom_props=[
            ('product:price:amount', str(product.precio_oferta)),
            ('product:price:currency', 'CLP'),
            ('product:availability', 'in stock' if product.stock > 0 else 'out of stock'),
            ('product:condition', 'new'),
        ]
    )
    
    precio_transferencia = product.precio * Decimal('0.97')
    precio_normal = product.precio * Decimal('1.03')
    descuento_porcentaje = 3
    imagenes_adicionales = product.imagenes_adicionales.all()
    producto_disponible = product.activo and product.stock > 0
    cliente_logueado = None
    if request.session.get('user_type') == 'cliente':
        try:
            cliente_logueado = Cliente.objects.get(id_cliente=request.session.get('cliente_id'))
        except Cliente.DoesNotExist:
            pass 
    if request.method == 'POST' and 'submit_comentario' in request.POST:
        if not cliente_logueado:
            messages.error(request, 'Debes iniciar sesión para dejar un comentario.')
            return redirect('login')
        
        form_comentario = ComentarioForm(request.POST)
        if form_comentario.is_valid():
            nuevo_comentario = form_comentario.save(commit=False)
            nuevo_comentario.producto = product
            nuevo_comentario.cliente = cliente_logueado
            nuevo_comentario.save()
            messages.success(request, '¡Gracias por tu comentario! Será revisado por un administrador antes de publicarse.')
            return redirect('product_detail', product_id=product_id)
        else:
            messages.error(request, 'Error al enviar tu comentario. Revisa los campos.')
    else:
        form_comentario = ComentarioForm()
    comentarios = product.comentarios.filter(aprobado=True)
    
    total_reseñas = comentarios.count()
    promedio_estrellas = 0
    if total_reseñas > 0:
        promedio_estrellas = comentarios.aggregate(Avg('estrellas'))['estrellas__avg']

    context = {
        'product': product,
        'precio_transferencia': precio_transferencia,
        'precio_normal': precio_normal,
        'descuento_porcentaje': descuento_porcentaje,
        'imagenes_adicionales': imagenes_adicionales,
        'meta': meta,  # Agregar meta al contexto
        'producto_disponible': producto_disponible,
        'comentarios': comentarios,
        'total_reseñas': total_reseñas,
        'promedio_estrellas': round(promedio_estrellas, 1) if promedio_estrellas else 0,
        'form_comentario': form_comentario,
        'cliente_logueado': cliente_logueado
    }
    return render(request, 'store/product_detail.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    if not product.activo:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        error_message = 'Este producto no está disponible actualmente.'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_message})
        else:
            messages.error(request, error_message)
            return redirect('product_detail', product_id=product_id)
    
    if product.stock <= 0:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        error_message = 'Este producto está agotado.'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_message})
        else:
            messages.error(request, error_message)
            return redirect('product_detail', product_id=product_id)
    
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    product_id_str = str(product.id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity}
    
    request.session['cart'] = cart
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        cart_items_data = []
        total_price = Decimal('0.00')
        product_ids = cart.keys()
        products_in_cart = Producto.objects.filter(id__in=product_ids)

        for p in products_in_cart:
            pid_str = str(p.id)
            qty = cart[pid_str]['quantity']
            precio_actual = p.precio_oferta
            
            total_price += precio_actual * qty
            
            cart_items_data.append({
                'id': p.id,
                'name': p.nombre,
                'quantity': qty,
                'price': float(precio_actual), 
                'image_url': p.imagen.url if p.imagen else '/static/img/no-image.png' 
            })

        return JsonResponse({
            'success': True,
            'cart_item_count': len(cart),
            'items': cart_items_data,
            'subtotal': float(total_price) 
        })
    else:
        if request.POST.get('next') == 'checkout':
            return redirect('checkout')
        return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products_in_cart = Producto.objects.filter(id__in=product_ids)

    cart_items = []
    total_transferencia = Decimal('0.00')
    total_otros_medios = Decimal('0.00')

    for product in products_in_cart:
        product_id_str = str(product.id)
        quantity = cart[product_id_str]['quantity']
        precio_transf_unitario = product.precio_transferencia
        precio_oferta_unitario = product.precio_oferta
        subtotal_transf = precio_transf_unitario * quantity
        subtotal_otros = precio_oferta_unitario * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal_transferencia': subtotal_transf,
            'subtotal_otros_medios': subtotal_otros, 
        })
        total_transferencia += subtotal_transf
        total_otros_medios += subtotal_otros

    context = {
        'cart_items': cart_items,
        'total_transferencia': total_transferencia,
        'total_otros_medios': total_otros_medios,
    }
    return render(request, 'store/cart.html', context)

def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if request.method == 'POST' and product_id_str in cart:
        action = request.POST.get('action')
        if action == 'increase':
            cart[product_id_str]['quantity'] += 1
        elif action == 'decrease':
            cart[product_id_str]['quantity'] -= 1
            if cart[product_id_str]['quantity'] <= 0:
                del cart[product_id_str]
    
    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    request.session['cart'] = cart
    return redirect('view_cart')

def clear_cart(request):
    if request.method == 'POST':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        return JsonResponse({'success': True, 'message': 'El carrito ha sido vaciado.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        correo = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if not correo or not password:
            return JsonResponse({
                'success': False,
                'message': 'Por favor, completa todos los campos.'
            })
        
        try:
            validate_email(correo)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de correo electrónico inválido.'
            })
        
        if len(password) < 6:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres.'
            })
        try:
            empleado = Empleado.objects.get(email=correo)
            if not empleado.activo:
                return JsonResponse({
                    'success': False,
                    'message': 'Tu cuenta ha sido desactivada. Contacta al administrador.'
                })
            
            if check_password(password, empleado.pass_hash):
                request.session['empleado_id'] = empleado.id_empleado
                request.session['empleado_nombre'] = empleado.nombre
                request.session['empleado_cargo'] = empleado.cargo
                request.session['user_type'] = 'empleado'
                request.session['is_superadmin'] = empleado.is_superadmin  # <-- AÑADIR ESTO
                
                return JsonResponse({
                    'success': True,
                    'message': f'¡Bienvenido, {empleado.nombre}! ({empleado.cargo})',
                    'redirect_url': '/gestion/' 
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Correo o contraseña incorrectos.'
                })
                
        except Empleado.DoesNotExist:
            try:
                cliente = Cliente.objects.get(email=correo)
                
                if check_password(password, cliente.pass_hash):
                    request.session['cliente_id'] = cliente.id_cliente
                    request.session['cliente_nombre'] = cliente.nombre
                    request.session['user_type'] = 'cliente'  
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'¡Bienvenido de vuelta, {cliente.nombre}!',
                        'redirect_url': '/'  
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Correo o contraseña incorrectos.'
                    })
                        
            except Cliente.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Correo o contraseña incorrectos.'
                })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor. Intenta de nuevo.'
            })

def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':

        rut = request.POST.get('rut', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        # Validaciones del backend
        
        # 1. Validar campos vacíos
        if not all([rut, nombre, apellido, correo, telefono, password, password2]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        # 2. Validar RUT chileno
        try:
            validate_chilean_rut(rut)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('register')

        # 3. Verificar si el RUT ya existe
        if Cliente.objects.filter(rut=rut).exists():
            messages.error(request, 'El RUT ya está registrado en el sistema.')
            return redirect('register')

        # 4. Validar formato de nombres (solo letras y espacios)
        name_regex = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(name_regex, nombre):
            messages.error(request, 'El nombre solo debe contener letras y espacios.')
            return redirect('register')
        
        if not re.match(name_regex, apellido):
            messages.error(request, 'El apellido solo debe contener letras y espacios.')
            return redirect('register')

        # 5. Validar longitud de nombres
        if len(nombre) < 2 or len(nombre) > 50:
            messages.error(request, 'El nombre debe tener entre 2 y 50 caracteres.')
            return redirect('register')
        
        if len(apellido) < 2 or len(apellido) > 100:
            messages.error(request, 'El apellido debe tener entre 2 y 100 caracteres.')
            return redirect('register')

        # 6. Validar formato de email
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'Formato de correo electrónico inválido.')
            return redirect('register')

        # 7. Validar longitud del email
        if len(correo) > 100:
            messages.error(request, 'El correo electrónico es demasiado largo.')
            return redirect('register')

        # 8. Verificar si el correo ya existe
        if Cliente.objects.filter(email=correo).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return redirect('register')

        # 9. Validar contraseñas coincidentes
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        # 10. Validar seguridad de contraseña
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('register')
        
        if not re.search(r'[a-z]', password):
            messages.error(request, 'La contraseña debe contener al menos una letra minúscula.')
            return redirect('register')
        
        if not re.search(r'[A-Z]', password):
            messages.error(request, 'La contraseña debe contener al menos una letra mayúscula.')
            return redirect('register')
        
        if not re.search(r'\d', password):
            messages.error(request, 'La contraseña debe contener al menos un número.')
            return redirect('register')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?~`]', password):
            messages.error(request, 'La contraseña debe contener al menos un carácter especial.')
            return redirect('register')
        
        # 11. Validar teléfono chileno
        if not re.match(r'^9\d{8}$', telefono):
            messages.error(request, 'El número de teléfono debe tener 9 dígitos y comenzar con 9 (formato chileno).')
            return redirect('register')

        try:
            hashed_password = make_password(password)

            nuevo_cliente = Cliente(
                rut=rut,
                nombre=nombre,
                apellidos=apellido,
                email=correo,
                telefono=telefono,
                pass_hash=hashed_password
            )

            nuevo_cliente.save()
            
            messages.success(request, '¡Tu cuenta ha sido creada con éxito! Ya puedes iniciar sesión.')
            return redirect('login')
        
        except IntegrityError as e:
            if 'rut' in str(e).lower():
                messages.error(request, 'El RUT ya está en uso.')
            elif 'UNIQUE constraint' in str(e) or 'unique' in str(e).lower():
                messages.error(request, 'El correo electrónico ya está en uso.')
            else:
                messages.error(request, 'Error al crear la cuenta. Por favor, intenta de nuevo.')
            return redirect('register')
        
        except Exception as e:
            messages.error(request, 'Ocurrió un error inesperado al crear tu cuenta. Contacta a soporte.')
            return redirect('register')

def logout_view(request):
    if request.method == 'POST':
        # Limpiar manualmente las variables de sesión personalizadas
        request.session.pop('empleado_id', None)
        request.session.pop('empleado_nombre', None)
        request.session.pop('empleado_cargo', None)
        request.session.pop('cliente_id', None)
        request.session.pop('cliente_nombre', None)
        request.session.pop('user_type', None)
        
        # Llamar al logout de Django
        logout(request)
        
        # IMPORTANTE: Forzar guardado de sesión modificada
        request.session.modified = True
        
        messages.success(request, '¡Has cerrado sesión exitosamente!')
        
        # Redirigir con parámetro para evitar caché
        from django.http import HttpResponseRedirect
        response = HttpResponseRedirect('/')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
        
    return redirect('home')

@admin_required
def panel_gestion_view(request):
    try:
        empleado = Empleado.objects.get(id_empleado=request.session.get('empleado_id'))
    except Empleado.DoesNotExist:
        # Si por alguna razón el empleado no existe, redirigir al login.
        messages.error(request, "No se pudo encontrar tu perfil de empleado.")
        return redirect('login')
        
    context = {
        'empleado': empleado
    }
    return render(request, 'gestion/panel.html', context)

@admin_required
def crear_categoria_view(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Categoría creada exitosamente!')
            return redirect('panel_gestion')
    else:
        form = CategoriaForm()
    
    return render(request, 'gestion/crear_form.html', {
        'form': form,
        'titulo': 'Crear Nueva Categoría'
    })

@admin_required
def crear_marca_view(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Marca creada exitosamente!')
            return redirect('panel_gestion')
    else:
        form = MarcaForm()

    return render(request, 'gestion/crear_form.html', {
        'form': form,
        'titulo': 'Crear Nueva Marca'
    })

@admin_required
def crear_producto_view(request):
    if request.method == 'POST':
        # Para formularios con archivos, se usa request.POST y request.FILES
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar temporalmente el valor antes de guardar el formulario
            publicar_redes = form.cleaned_data.get('publicar_redes', False)
            
            # Guardar el producto SIN commit para asignar el flag primero
            producto = form.save(commit=False)
            
            # Almacenar el flag en el objeto ANTES de guardarlo
            producto._publicar_redes = publicar_redes
            
            # Ahora sí guardar (esto dispara el signal CON el flag ya asignado)
            producto.save()
            
            messages.success(request, '¡Producto creado exitosamente!')
            return redirect('panel_gestion')
    else:
        form = ProductoForm()

    return render(request, 'gestion/crear_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo Producto'
    })
    
def listar_productos_view(request):
    productos_list = Producto.objects.all().order_by('id')
    
    # Lógica de paginación
    paginator = Paginator(productos_list, 8) # Muestra 8 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gestion/productos_list.html', {'page_obj': page_obj})


# ...
@admin_required
def editar_producto_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        
        # ¡AQUÍ OCURRE LA VALIDACIÓN!
        if form.is_valid():
            form.save() # Solo se guarda si los datos son válidos
            messages.success(request, f'¡Producto "{producto.nombre}" actualizado exitosamente!')
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'gestion/editar_form.html', { # Si no es válido, se vuelve a mostrar el formulario con los errores
        'form': form,
        'titulo': f'Editar Producto: {producto.nombre}',
        'objeto_id': producto.id,
        'volver_url': 'listar_productos'
    })

# @admin_required
def eliminar_producto_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        # Devuelve una respuesta JSON en lugar de redirigir
        return JsonResponse({'success': True, 'message': f'Producto "{nombre_producto}" eliminado exitosamente.'})
    # Si no es POST, no hagas nada (o devuelve un error)
    return JsonResponse({'success': False, 'message': 'Petición no válida.'})

# --- VISTAS PARA CATEGORÍAS ---

# @admin_required
def listar_categorias_view(request):
    categorias_list = Categoria.objects.all().order_by('id')
    paginator = Paginator(categorias_list, 8) # 8 ítems por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gestion/categorias_list.html', {'page_obj': page_obj})

# @admin_required
def editar_categoria_view(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Categoría "{categoria.nombre}" actualizada exitosamente!')
            return redirect('listar_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'gestion/editar_form.html', {
        'form': form,
        'titulo': f'Editar Categoría: {categoria.nombre}',
        'objeto_id': categoria.id,
        'volver_url': 'listar_categorias'
    })

# @admin_required
def eliminar_categoria_view(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre_categoria = categoria.nombre
        categoria.delete()
        return JsonResponse({'success': True, 'message': f'Categoría "{nombre_categoria}" eliminada exitosamente.'})
    return JsonResponse({'success': False, 'message': 'Petición no válida.'})

# --- VISTAS PARA MARCAS ---

# @admin_required
def listar_marcas_view(request):
    marcas_list = Marca.objects.all().order_by('id')
    paginator = Paginator(marcas_list, 8) # 8 ítems por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gestion/marcas_list.html', {'page_obj': page_obj})


# @admin_required
def editar_marca_view(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Marca "{marca.nombre}" actualizada exitosamente!')
            return redirect('listar_marcas')
    else:
        form = MarcaForm(instance=marca)
    
    return render(request, 'gestion/editar_form.html', {
        'form': form,
        'titulo': f'Editar Marca: {marca.nombre}',
        'objeto_id': marca.id,
        'volver_url': 'listar_marcas'
    })

# @admin_required
def eliminar_marca_view(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        nombre_marca = marca.nombre
        marca.delete()
        return JsonResponse({'success': True, 'message': f'Marca "{nombre_marca}" eliminada exitosamente.'})
    return JsonResponse({'success': False, 'message': 'Petición no válida.'})

    
def exportar_productos_csv(request):
    """
    Genera un archivo CSV con todos los productos y lo ofrece para descarga.
    """
    # 1. Prepara la respuesta HTTP
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="productos_techtop.csv"'},
    )
    # Para que el CSV se lea correctamente con caracteres en español
    response.write(u'\ufeff'.encode('utf8'))

    # 2. Crea un "escritor" de CSV
    writer = csv.writer(response)

    # 3. Escribe la fila del encabezado
    writer.writerow(['ID', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría', 'Marca'])

    # 4. Obtiene todos los productos y escribe sus datos
    # Usamos select_related para optimizar la consulta a la base de datos
    productos = Producto.objects.select_related('categoria', 'marca').all()
    for producto in productos:
        writer.writerow([
            producto.id,
            producto.nombre,
            producto.descripcion,
            producto.precio,
            producto.stock,
            producto.categoria.nombre,
            producto.marca.nombre,
        ])

    # 5. Devuelve la respuesta con el archivo generado
    return response

def exportar_categorias_csv(request):
    """
    Genera un archivo CSV con todas las categorías.
    """
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="categorias_techtop.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8')) # Para compatibilidad con caracteres en español

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Descripción'])

    for categoria in Categoria.objects.all():
        writer.writerow([categoria.id, categoria.nombre, categoria.descripcion])

    return response

# @admin_required
def exportar_marcas_csv(request):
    """
    Genera un archivo CSV con todas las marcas.
    """
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="marcas_techtop.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre'])

    for marca in Marca.objects.all():
        writer.writerow([marca.id, marca.nombre])

    return response


def audio_video_catalog(request):
    # Obtener productos y filtros seleccionados
    products = Producto.objects.filter(categoria__nombre='Audio-y-Video')
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    # Aplicar filtros
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    # Obtener marcas disponibles
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')


    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'audio_video',
        'category_title': 'Audio y Video'
    }
    
    return render(request, 'store/tienda.html', context)

def seguridad_sensores_catalog(request):
    # Obtener productos y filtros seleccionados
    products = Producto.objects.filter(categoria__nombre='Seguridad-y-Sensores')
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    # Aplicar filtros
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    # Obtener marcas disponibles
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')



    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'seguridad_sensores',
        'category_title': 'Seguridad y Sensores'
    }
    
    return render(request, 'store/tienda.html', context)

def diagnostico_catalog(request):
    # Obtener productos y filtros seleccionados
    products = Producto.objects.filter(categoria__nombre='Diagnostico-Automotriz')
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    # Aplicar filtros
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    # Obtener marcas disponibles
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')


    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'diagnostico',
        'category_title': 'Diagnóstico Automotriz'
    }
    
    return render(request, 'store/tienda.html', context)

def herramientas_medicion_catalog(request):
    # Obtener productos y filtros seleccionados
    products = Producto.objects.filter(categoria__nombre='Herramientas-de-Medicion')
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    # Aplicar filtros
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    # Obtener marcas disponibles
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')



    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'herramientas_medicion',
        'category_title': 'Herramientas de Medición'
    }
    
    return render(request, 'store/tienda.html', context)

def medidores_catalog(request):
    # Obtener productos y filtros seleccionados
    products = Producto.objects.filter(categoria__nombre='Medidores')
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    # Aplicar filtros
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    # Obtener marcas disponibles
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')



    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'medidores',
        'category_title': 'Medidores'
    }
    
    return render(request, 'store/tienda.html', context)

def electronica_automotriz_catalog(request):
    # Obtener productos y filtros seleccionados
    products = Producto.objects.filter(categoria__nombre='Electronica-Automotriz')
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    # Aplicar filtros
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    # Obtener marcas disponibles
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')

    # Calcular precio de transferencia


    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'electronica_automotriz',
        'category_title': 'Electrónica Automotriz'
    }
    
    return render(request, 'store/tienda.html', context)

def electronica_general_catalog(request):
    # Obtener productos y filtros seleccionados
    products = Producto.objects.filter(categoria__nombre='Electronica-General')
    selected_brands = request.GET.getlist('marca')
    selected_prices = request.GET.getlist('precio')

    # Aplicar filtros
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)

    if selected_prices:
        price_queries = Q()
        for price_range in selected_prices:
            min_price, max_price = price_range.split('-')
            price_queries |= Q(precio__range=(min_price, max_price))
        products = products.filter(price_queries)

    # Obtener marcas disponibles
    available_brands = Marca.objects.filter(
        producto__in=products
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')


    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'electronica_general',
        'category_title': 'Electrónica General'
    }
    
    return render(request, 'store/tienda.html', context)

def search_results_view(request):
    """
    Filtra los productos basándose en la consulta de búsqueda y muestra los resultados.
    """
    query = request.GET.get('q', '') 
    products = None

    if query:
        products = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(marca__nombre__icontains=query)
        ).distinct()

    # SEO para resultados de búsqueda
    if query:
        meta = Meta(
            title=f"Resultados para '{query}' - Techtop",
            description=f"Resultados de búsqueda para '{query}' en Techtop. Encuentra los mejores productos de tecnología y electrónica en Chile.",
            keywords=[query.lower(), 'búsqueda', 'techtop', 'productos', 'chile'],
            url=request.build_absolute_uri(),
            object_type='website'
        )
    else:
        meta = Meta(
            title="Búsqueda de Productos - Techtop",
            description="Busca productos en nuestro catálogo. Encuentra radios Android, electrónica automotriz y tecnología en Techtop.",
            keywords=['búsqueda', 'productos', 'techtop', 'catálogo', 'chile'],
            url=request.build_absolute_uri(),
            object_type='website'
        )

    context = {
        'products': products,
        'search_query': query,
        'meta': meta
    }
    return render(request, 'store/search_results.html', context)

# store/views.py

def checkout_view(request):
    """
    Muestra la página de checkout con los precios correctos (oferta base + transferencia).
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Tu carro está vacío.')
        return redirect('view_cart')

    product_ids = cart.keys()
    products_in_cart = Producto.objects.filter(id__in=product_ids)
    
    cart_items = []
    total_transferencia = Decimal('0.00')
    total_otros_medios = Decimal('0.00')

    for product in products_in_cart:
        product_id_str = str(product.id)
        quantity = cart[product_id_str]['quantity']
        
        # --- USAMOS LAS NUEVAS PROPIEDADES DEL MODELO ---
        # precio_transferencia: Ya incluye la oferta base (si existe) + 3% extra.
        # precio_oferta: Es el precio base con el descuento del slider aplicado.
        
        precio_transf_unitario = product.precio_transferencia
        precio_oferta_unitario = product.precio_oferta

        # Calculamos subtotales por línea de producto
        subtotal_transf = precio_transf_unitario * quantity
        subtotal_otros = precio_oferta_unitario * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal_transferencia': subtotal_transf,
            'subtotal_otros_medios': subtotal_otros,
        })
        
        # Acumulamos a los totales generales
        total_transferencia += subtotal_transf
        total_otros_medios += subtotal_otros

    # --- Lógica de pre-llenado del formulario con datos del usuario logueado ---
    initial_data = {}
    user_type = request.session.get('user_type')
    
    if user_type == 'cliente':
        cliente_id = request.session.get('cliente_id')
        if cliente_id:
            try:
                user = Cliente.objects.get(id_cliente=cliente_id)
                initial_data = {
                    'nombre': user.nombre,
                    'apellidos': user.apellidos,
                    'rut': getattr(user, 'rut', ''),
                    'email': user.email,
                    'telefono': user.telefono,
                }
            except Cliente.DoesNotExist:
                pass
                
    elif user_type == 'empleado':
        empleado_id = request.session.get('empleado_id')
        if empleado_id:
            try:
                user = Empleado.objects.get(id_empleado=empleado_id)
                initial_data = {
                    'nombre': user.nombre,
                    'apellidos': user.apellidos,
                    'rut': getattr(user, 'rut', ''),
                    'email': user.email,
                    'telefono': user.telefono,
                }
            except Empleado.DoesNotExist:
                pass

    form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_transferencia': total_transferencia,
        'total_otros_medios': total_otros_medios,
    }
    return render(request, 'store/checkout.html', context)


# --- VISTA PARA PROCESAR EL PEDIDO (SIN CAMPOS *_cliente) ---
@transaction.atomic
def procesar_pedido_view(request):
    """
    Procesa el pedido usando los precios correctos según el método de pago elegido.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})

    cart = request.session.get('cart', {})
    if not cart:
        return JsonResponse({'success': False, 'message': 'Tu carro está vacío.'})

    form = CheckoutForm(request.POST)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        metodo_pago = cleaned_data.get('metodo_pago')
        tipo_entrega = cleaned_data.get('tipo_entrega')

        # --- 1. OBTENER DATOS Y VALIDAR STOCK ---
        product_ids = cart.keys()
        # Usamos select_for_update para bloquear los registros mientras descontamos stock
        products_in_cart = Producto.objects.select_for_update().filter(id__in=product_ids)
        
        cart_items_details = []
        subtotal_calculado = Decimal('0')
        
        product_map = {str(p.id): p for p in products_in_cart}

        for product_id_str, item_data in cart.items():
            product = product_map.get(product_id_str)
            if not product:
                return JsonResponse({'success': False, 'message': f'Producto ID {product_id_str} no disponible.'})
            
            quantity = item_data['quantity']
            if product.stock < quantity:
                return JsonResponse({'success': False, 'message': f'Stock insuficiente para "{product.nombre}".'})

            # --- CAMBIO CLAVE: DETERMINAR PRECIO FINAL A GUARDAR ---
            # Si paga con transferencia, usamos el precio que ya incluye oferta + 3% extra.
            # Si paga con otro medio, usamos el precio oferta (que puede ser igual al normal si el descuento es 0%).
            if metodo_pago == 'transferencia':
                precio_final_unitario = product.precio_transferencia
            else:
                precio_final_unitario = product.precio_oferta
            
            cart_items_details.append({
                'producto': product,
                'cantidad': quantity,
                'precio_unitario': precio_final_unitario
            })
            subtotal_calculado += precio_final_unitario * quantity

        # --- 2. BUSCAR CLIENTE (Si está logueado) ---
        cliente_obj = None
        if request.session.get('user_type') == 'cliente':
            try:
                cliente_obj = Cliente.objects.get(id_cliente=request.session.get('cliente_id'))
            except Cliente.DoesNotExist:
                pass # Si no existe, el pedido quedará como anónimo (o podrías forzar logout)

        # --- 3. MANEJAR DIRECCIÓN Y COSTO DE ENVÍO ---
        direccion_obj = None
        costo_envio_calculado = Decimal('0')
        
        if tipo_entrega == 'delivery':
            costo_envio_calculado = Decimal('4500') # Costo fijo por ahora
            # Si el cliente está registrado, guardamos la dirección
            if cliente_obj:
                 try:
                     # Podrías mejorar esto para no crear duplicados si la dirección ya existe
                     direccion_obj = Direccion.objects.create(
                        cliente=cliente_obj,
                        calle=cleaned_data.get('calle'),
                        numero=cleaned_data.get('numero', ''),
                        # Depto/Casa y Comuna se podrían agregar al modelo Direccion si lo actualizas
                        ciudad='Santiago',    # Valor por defecto si no está en el formulario
                        region='Metropolitana', # Valor por defecto
                        codigo_postal=cleaned_data.get('codigo_postal', '')
                     )
                 except Exception as e:
                      print(f"Advertencia: No se pudo guardar la dirección: {e}")
                      # El pedido sigue adelante, pero sin dirección guardada en BD (solo en el pedido físico si lo requieres)

        # --- 4. CALCULAR TOTAL FINAL ---
        total_pedido = subtotal_calculado + costo_envio_calculado

        # --- 5. CREAR EL PEDIDO ---
        try:
            nuevo_pedido = Pedido.objects.create(
                cliente=cliente_obj,
                direccion_envio=direccion_obj,
                total=total_pedido,
                estado='pendiente',
                metodo_pago=metodo_pago
                # fecha_pedido y tracking_number se generan automáticamente
            )
        except Exception as e:
             return JsonResponse({'success': False, 'message': 'Error interno al crear el pedido. Intenta nuevamente.'})

        # --- 6. GUARDAR DETALLES Y ACTUALIZAR STOCK ---
        for item in cart_items_details:
            DetallePedido.objects.create(
                pedido=nuevo_pedido,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'] # Guardamos el precio exacto que se cobró
            )
            # Descontar stock
            producto = item['producto']
            producto.stock -= item['cantidad']
            producto.save() # El método save() del modelo ya maneja el campo 'activo' si stock llega a 0

        # --- 7. FINALIZAR: LIMPIAR CARRO (Solo si no es pago externo inmediato) ---
        # Si es transferencia, ya "terminó" la compra online, así que limpiamos el carro.
        # Si es Webpay/MercadoPago, esperamos a la confirmación para limpiar.
        if metodo_pago == 'transferencia':
             if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

        # --- 8. REDIRECCIONAR SEGÚN MÉTODO DE PAGO ---
        if metodo_pago == 'webpay':
            return JsonResponse({
                'success': True,
                'message': 'Redirigiendo a Webpay...',
                'redirect_url': reverse('iniciar_pago_webpay', args=[nuevo_pedido.id])
            })
        elif metodo_pago == 'mercadopago':
            return JsonResponse({
                'success': True,
                'message': 'Redirigiendo a Mercado Pago...',
                'redirect_url': reverse('iniciar_pago_mercadopago', args=[nuevo_pedido.id])
            })
        elif metodo_pago == 'transferencia':
            # Redirigir a la página de subir comprobante
            return JsonResponse({
                'success': True,
                'message': 'Pedido creado correctamente. Redirigiendo para finalizar...',
                'redirect_url': reverse('subir_comprobante', args=[nuevo_pedido.id])
            })
        else:
            # Fallback para otros métodos futuros
            return JsonResponse({
                'success': True,
                'message': 'Pedido creado exitosamente.',
                'redirect_url': reverse('generar_recibo_pdf', args=[nuevo_pedido.id])
            })

    else:
        # Errores de validación del formulario
        first_error = next(iter(form.errors.values()))[0] if form.errors else "Revisa los datos ingresados."
        return JsonResponse({ 'success': False, 'message': f'Error en el formulario: {first_error}' })

def generar_recibo_pdf(request, pedido_id):
    """
    Genera un recibo en PDF para un pedido REAL desde la BD.
    Obtiene datos del cliente SÓLO si hay un Cliente asociado.
    """
    try:
        # Buscamos el pedido y precargamos datos relacionados
        pedido = Pedido.objects.select_related('cliente', 'direccion_envio').get(id=pedido_id)
        detalles = pedido.detalles.select_related('producto').all()
    except Pedido.DoesNotExist:
        raise Http404("Pedido no encontrado")

    # --- OBTENER DATOS DEL CLIENTE (CORREGIDO: SÓLO DESDE pedido.cliente) ---
    # Valores por defecto si no hay cliente asociado
    cliente_nombre_completo = 'Cliente no registrado'
    cliente_email = 'No disponible'
    cliente_rut = 'No disponible'

    # Si SÍ hay un objeto Cliente asociado al pedido, usamos sus datos
    if pedido.cliente:
        cliente_nombre_completo = f"{pedido.cliente.nombre} {pedido.cliente.apellidos}"
        cliente_email = pedido.cliente.email
        # Asumiendo que tu modelo Cliente tiene el campo 'rut'
        cliente_rut = getattr(pedido.cliente, 'rut', 'No disponible') # Usamos getattr por seguridad


    # --- CÁLCULOS (sin cambios) ---
    subtotal = sum(d.precio_unitario * d.cantidad for d in detalles)
    total_iva = subtotal * Decimal('0.19') # Asumiendo IVA 19%
    # Inferimos costo envío basado en si hay dirección guardada
    costo_envio = Decimal('4500') if pedido.direccion_envio else Decimal('0.00')
    total_pagado = pedido.total # Usamos el total guardado

    logo_path = request.build_absolute_uri(settings.STATIC_URL + 'img/new_black.png')

    context = {
        'pedido': pedido, # Objeto Pedido completo
        'detalles': detalles, # Lista de DetallePedido reales
        'cliente_nombre_completo': cliente_nombre_completo, # Dato corregido
        'cliente_email': cliente_email, # Dato corregido
        'cliente_rut': cliente_rut, # Dato corregido
        'subtotal': subtotal,
        'total_iva': total_iva,
        'costo_envio': costo_envio, # Costo inferido
        'total_pagado': total_pagado, # Total del pedido
        'logo_path': logo_path,
        'fecha_actual': timezone.now()
    }

    # --- GENERACIÓN PDF (sin cambios) ---
    template = get_template('store/recibo_pdf.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recibo_techtop_{pedido.id}.pdf"'
        return response
    else:
        return HttpResponse(f"Error al generar el PDF: {pdf.err}. Revisa los logs.", status=500)





# ==================== INTEGRACIÓN CON TRANSBANK WEBPAY PLUS ====================

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
import uuid

def _configurar_transbank():
    """Configura el SDK de Transbank según el ambiente (integración/producción)"""
    if settings.TRANSBANK_ENVIRONMENT == 'PRODUCCION':
        Transaction.commerce_code = settings.TRANSBANK_COMMERCE_CODE
        Transaction.api_key = settings.TRANSBANK_API_KEY
        Transaction.integration_type = IntegrationType.LIVE
    else:
        # Ambiente de integración (pruebas)
        Transaction.commerce_code = settings.TRANSBANK_COMMERCE_CODE
        Transaction.api_key = settings.TRANSBANK_API_KEY
        Transaction.integration_type = IntegrationType.TEST


@transaction.atomic
def iniciar_pago_webpay(request, pedido_id):
    """
    Inicia el proceso de pago con Webpay Plus.
    Crea el token y redirige al usuario a Transbank.
    """

    try:
        # Obtener el pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        # Verificar que no exista ya una transacción autorizada para este pedido
        transaccion_existente = TransaccionWebpay.objects.filter(
            pedido=pedido, 
            estado='AUTORIZADO'
        ).first()
        
        if transaccion_existente:
            messages.warning(request, 'Este pedido ya fue pagado.')
            return redirect('generar_recibo_pdf', pedido_id=pedido.id)
        
        _configurar_transbank()
        
        # Generar un buy_order único
        buy_order = f"ORD-{pedido.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # Obtener el monto (convertir a entero, Transbank no acepta decimales)
        monto = int(pedido.total)

        
        # URLs de retorno
        return_url = request.build_absolute_uri(reverse('retorno_webpay'))
        
        # Crear la transacción en Webpay
        # El SDK v4.0.0 usa esta firma: create(buy_order, session_id, amount, return_url)
        tx = Transaction()
        response = tx.create(buy_order, str(request.session.session_key or 'SESSION'), monto, return_url)
        
        # Guardar la transacción en la base de datos
        transaccion = TransaccionWebpay.objects.create(
            pedido=pedido,
            token=response['token'],
            buy_order=buy_order,
            monto=pedido.total,
            estado='PENDIENTE'
        )
        
        # Guardar el token en la sesión para validar posteriormente
        request.session[f'webpay_token_{pedido.id}'] = response['token']
        
        # Construir la URL de Webpay
        webpay_url = response['url'] + '?token_ws=' + response['token']
        
        # Redirigir al usuario a Webpay
        return redirect(webpay_url)
        
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('checkout')


@transaction.atomic
def retorno_webpay(request):
    """
    Vista que recibe el retorno desde Webpay después del pago.
    Confirma la transacción y actualiza el estado del pedido.
    """
    token_ws = request.GET.get('token_ws') or request.POST.get('token_ws')
    
    
    if not token_ws:
        messages.error(request, 'Token de transacción no válido.')
        return redirect('home')
    
    try:
        # Configurar Transbank
        _configurar_transbank()
        
        tx = Transaction()
        response = tx.commit(token_ws)
        
        # Buscar la transacción en la base de datos
        transaccion = TransaccionWebpay.objects.filter(token=token_ws).first()
        
        if not transaccion:
            messages.error(request, 'Transacción no encontrada.')
            return redirect('home')
        
        # Actualizar la transacción con los datos de respuesta
        transaccion.response_code = str(response.get('response_code', ''))
        transaccion.authorization_code = response.get('authorization_code', '')
        transaccion.payment_type_code = response.get('payment_type_code', '')
        
        # Obtener últimos 4 dígitos de la tarjeta si están disponibles
        if 'card_detail' in response and 'card_number' in response['card_detail']:
            transaccion.card_number = response['card_detail']['card_number']
        
        # Verificar si el pago fue aprobado
        if response.get('response_code') == 0 and response.get('status') == 'AUTHORIZED':
            transaccion.estado = 'AUTORIZADO'
            transaccion.save()
            
            # Actualizar el estado del pedido
            pedido = transaccion.pedido
            pedido.estado = 'procesando'
            pedido.save()
            
            # Limpiar el carrito
            if 'cart' in request.session:
                del request.session['cart']
            
            enviar_recibo_por_email(pedido)
            
            messages.success(request, '¡Pago realizado exitosamente!')
            
            # Renderizar página de confirmación
            context = {
                'pedido': pedido,
                'transaccion': transaccion,
                'exito': True,
                'response': response
            }
            return render(request, 'store/confirmacion_pago.html', context)
        else:
            # Pago rechazado
            transaccion.estado = 'RECHAZADO'
            transaccion.save()
            
            # Opcional: Actualizar estado del pedido
            pedido = transaccion.pedido
            pedido.estado = 'cancelado'
            pedido.save()
            
            # Restaurar el stock de los productos
            for detalle in pedido.detalles.all():
                producto = detalle.producto
                producto.stock += detalle.cantidad
                producto.save()
            
            messages.error(request, 'El pago fue rechazado. Por favor, intenta nuevamente.')
            
            context = {
                'pedido': pedido,
                'transaccion': transaccion,
                'exito': False,
                'response': response
            }
            return render(request, 'store/confirmacion_pago.html', context)
            
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('home')


def anular_transaccion_webpay(request, transaccion_id):
    """
    Vista para anular una transacción de Webpay (solo para usuarios autorizados).
    """
    if request.session.get('user_type') != 'empleado':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('home')
    
    try:
        transaccion = get_object_or_404(TransaccionWebpay, id=transaccion_id)
        
        if transaccion.estado != 'AUTORIZADO':
            messages.warning(request, 'Solo se pueden anular transacciones autorizadas.')
            return redirect('panel_gestion')
        
        # Configurar Transbank
        _configurar_transbank()
        
        # Anular la transacción
        tx = Transaction()
        response = tx.refund(transaccion.token, int(transaccion.monto))
        
        if response.get('type') == 'REVERSED':
            transaccion.estado = 'ANULADO'
            transaccion.save()
            
            # Actualizar el pedido
            pedido = transaccion.pedido
            pedido.estado = 'cancelado'
            pedido.save()
            
            # Restaurar stock
            for detalle in pedido.detalles.all():
                producto = detalle.producto
                producto.stock += detalle.cantidad
                producto.save()
            
            messages.success(request, 'Transacción anulada exitosamente.')
        else:
            messages.error(request, 'No se pudo anular la transacción.')
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('panel_gestion')


# ==================== INTEGRACIÓN CON MERCADO PAGO ====================

import mercadopago

def _configurar_mercadopago():
    """Configura el SDK de Mercado Pago según el ambiente"""
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    return sdk


@transaction.atomic
def iniciar_pago_mercadopago(request, pedido_id):
    """
    Crea una preferencia de pago en Mercado Pago y redirige al usuario.
    """
    try:
        # Obtener el pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        # Verificar que no exista ya una transacción aprobada
        transaccion_existente = TransaccionMercadoPago.objects.filter(
            pedido=pedido,
            estado='approved'
        ).first()
        
        if transaccion_existente:
            messages.warning(request, 'Este pedido ya fue pagado.')
            return redirect('generar_recibo_pdf', pedido_id=pedido.id)
        
        sdk = _configurar_mercadopago()
        
        # Preparar items del pedido
        items = []
        for detalle in pedido.detalles.all():
            items.append({
                "title": detalle.producto.nombre,
                "quantity": detalle.cantidad,
                "unit_price": float(detalle.precio_unitario),
                "currency_id": "CLP"
            })
        
        
        # URLs de retorno
        success_url = request.build_absolute_uri(reverse('retorno_mercadopago_success'))
        failure_url = request.build_absolute_uri(reverse('retorno_mercadopago_failure'))
        pending_url = request.build_absolute_uri(reverse('retorno_mercadopago_pending'))
        
        
        # Crear preferencia de pago (sin auto_return por ahora)
        preference_data = {
            "items": items,
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url
            },
            "external_reference": str(pedido.id),
            "statement_descriptor": "TechTop"
        }
        
        preference_response = sdk.preference().create(preference_data)
        
        # Verificar si hay error en la respuesta
        if preference_response.get('status') != 201:
            error_msg = preference_response.get('response', {}).get('message', 'Error desconocido')
            raise Exception(f"Error de Mercado Pago: {error_msg}")
        
        # La respuesta exitosa viene en preference_response["response"]
        preference = preference_response["response"]
        
        
        # Guardar la transacción en la base de datos
        transaccion = TransaccionMercadoPago.objects.create(
            pedido=pedido,
            preference_id=preference['id'],
            monto=pedido.total,
            estado='pending'
        )
        
        # Obtener la URL de inicio de pago (usar sandbox para ambiente de pruebas)
        init_point = preference.get('sandbox_init_point') or preference.get('init_point')
        
        # Redirigir al usuario a Mercado Pago
        return redirect(init_point)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('checkout')


@transaction.atomic
def retorno_mercadopago_success(request):
    """Maneja el retorno exitoso desde Mercado Pago"""
    return _procesar_retorno_mercadopago(request, 'approved')


@transaction.atomic
def retorno_mercadopago_failure(request):
    """Maneja el retorno fallido desde Mercado Pago"""
    return _procesar_retorno_mercadopago(request, 'rejected')


@transaction.atomic
def retorno_mercadopago_pending(request):
    """Maneja el retorno pendiente desde Mercado Pago"""
    return _procesar_retorno_mercadopago(request, 'pending')


@superadmin_required
def test_seo(request):
    """Vista temporal para testear SEO con preview visual - SOLO SUPERADMIN"""
    # Obtener un producto de ejemplo
    producto = Producto.objects.filter(activo=True).first()
    
    if not producto:
        return HttpResponse("No hay productos disponibles para testear")
    
    from meta.views import Meta
    
    # Construir URL absoluta de la imagen
    image_url = None
    if producto.imagen:
        if producto.imagen.url.startswith('http'):
            image_url = producto.imagen.url
        else:
            image_url = request.build_absolute_uri(producto.imagen.url)
    
    meta = Meta(
        title=f"{producto.nombre} - Techtop",
        description=f"Compra {producto.nombre} al mejor precio en Techtop. Envío rápido a todo Chile. Stock disponible. ¡Aprovecha nuestras ofertas!",
        image=image_url,
        url=request.build_absolute_uri(),
        object_type='product',
        keywords=['techtop', producto.nombre.lower(), 'comprar', 'chile'],
        extra_custom_props=[
            ('product:price:amount', str(producto.precio_oferta)),
            ('product:price:currency', 'CLP'),
        ]
    )
    
    context = {
        'meta': meta,
        'producto': producto
    }
    
    return render(request, 'test_seo.html', context)


def _procesar_retorno_mercadopago(request, estado_esperado):
    """
    Procesa el retorno desde Mercado Pago.
    """
    
    # Obtener parámetros de la URL
    preference_id = request.GET.get('preference_id')
    payment_id = request.GET.get('payment_id')
    external_reference = request.GET.get('external_reference')
    
    
    try:
        # Buscar la transacción
        transaccion = None
        
        if payment_id:
            transaccion = TransaccionMercadoPago.objects.filter(payment_id=payment_id).first()
        
        if not transaccion and preference_id:
            transaccion = TransaccionMercadoPago.objects.filter(preference_id=preference_id).first()
        
        if not transaccion and external_reference:
            try:
                pedido_id = int(external_reference)
                transaccion = TransaccionMercadoPago.objects.filter(pedido_id=pedido_id).first()
            except ValueError:
                pass
        
        if not transaccion:
            messages.error(request, 'No se pudo verificar el estado del pago.')
            return redirect('home')
        
        pedido = transaccion.pedido
        
        # Si el pago ya fue procesado, redirigir
        if transaccion.estado == 'approved' and pedido.estado == 'procesando':
            messages.info(request, 'Este pago ya fue procesado.')
            return redirect('generar_recibo_pdf', pedido_id=pedido.id)
        
        # Configurar SDK
        sdk = _configurar_mercadopago()
        
        # Obtener información del pago
        if payment_id:

            payment_resource = sdk.payment()
            payment_data = payment_resource.get(int(payment_id))
            
            if 'response' in payment_data:
                payment_data = payment_data['response']
            
            
            # Actualizar la transacción
            transaccion.payment_id = str(payment_id)
            transaccion.estado = payment_data.get('status', 'unknown')
            transaccion.status_detail = payment_data.get('status_detail', '')
            
            if 'transaction_amount' in payment_data:
                transaccion.monto = Decimal(str(payment_data['transaction_amount']))
            
            transaccion.payment_method_id = payment_data.get('payment_method_id', '')
            transaccion.payment_type_id = payment_data.get('payment_type_id', '')
            
            if 'card' in payment_data and payment_data['card']:
                transaccion.card_last_four_digits = payment_data['card'].get('last_four_digits', '')
            
            if 'payer' in payment_data:
                transaccion.payer_email = payment_data['payer'].get('email', '')
                if 'identification' in payment_data['payer']:
                    transaccion.payer_identification = payment_data['payer']['identification'].get('number', '')
            
            transaccion.save()
            
            # Si fue aprobado
            if payment_data.get('status') == 'approved':
                pedido = transaccion.pedido
                pedido.estado = 'procesando'
                pedido.save()
                
                # Limpiar el carrito
                if 'cart' in request.session:
                    del request.session['cart']
                
                enviar_recibo_por_email(pedido)
                
                messages.success(request, '¡Pago realizado exitosamente!')
                return redirect('generar_recibo_pdf', pedido_id=pedido.id)
            else:
                messages.warning(request, 'El pago no se completó correctamente.')
                return redirect('checkout')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('home')

def obtener_ventas_en_tiempo(fecha_inicio, agrupador):
    """
    Obtiene las ventas agregadas por tiempo (día, mes o año).
    Filtra solo pedidos confirmados (no pendientes ni cancelados).
    """
    # Definimos qué estados consideramos como "ventas reales"
    estados_validos = ['procesando', 'enviado', 'entregado']
    
    ventas = Pedido.objects.filter(
        fecha_pedido__gte=fecha_inicio,
        estado__in=estados_validos
    ).annotate(
        periodo=agrupador('fecha_pedido')
    ).values('periodo').annotate(
        total_ventas=Sum('total')
    ).order_by('periodo')

    # Formatear para Chart.js
    labels = []
    values = []
    for venta in ventas:
        # Formato de fecha dependiendo del agrupador
        if isinstance(agrupador, type(TruncDay)):
            fecha_fmt = venta['periodo'].strftime("%d/%m") # Ej: 25/10
        elif isinstance(agrupador, type(TruncMonth)):
            fecha_fmt = venta['periodo'].strftime("%m/%Y") # Ej: 10/2025
        else:
            fecha_fmt = venta['periodo'].strftime("%Y") # Ej: 2025
            
        labels.append(fecha_fmt)
        values.append(float(venta['total_ventas']))

    return {'labels': labels, 'values': values}

def obtener_top_productos(fecha_inicio):
    """
    Obtiene el top 10 de productos más vendidos en un período.
    Ordena primero por cantidad vendida (descendente) y luego por ingresos generados (descendente) para desempatar.
    """
    estados_validos = ['procesando', 'enviado', 'entregado']
    
    top = DetallePedido.objects.filter(
        pedido__fecha_pedido__gte=fecha_inicio,
        pedido__estado__in=estados_validos
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        ingresos_totales=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-cantidad_total', '-ingresos_totales')[:10]  # <-- AQUÍ ESTÁ EL CAMBIO CLAVE

    return [
        {
            'name': item['producto__nombre'],
            'quantity': item['cantidad_total'],
            'revenue': float(item['ingresos_totales'])
        }
        for item in top
    ]

def obtener_metricas_envio(fecha_inicio):
    """
    Cuenta cuántos pedidos fueron con retiro vs delivery.
    """
    estados_validos = ['procesando', 'enviado', 'entregado']
    
    stats = Pedido.objects.filter(
        fecha_pedido__gte=fecha_inicio,
        estado__in=estados_validos
    ).aggregate(
        retiro=Count('id', filter=Q(direccion_envio__isnull=True)),
        delivery=Count('id', filter=Q(direccion_envio__isnull=False))
    )
    
    return {
        'pickup': stats['retiro'] or 0,
        'delivery': stats['delivery'] or 0
    }
    
def obtener_metricas_pago(fecha_inicio):
    """
    Cuenta cuántos pedidos pagados se hicieron con cada método.
    Se basa en las relaciones inversas y los estados de éxito de cada transacción.
    """
    estados_validos = ['procesando', 'enviado', 'entregado']
    
    # Filtramos los pedidos válidos en el rango de fecha
    pedidos = Pedido.objects.filter(
        fecha_pedido__gte=fecha_inicio,
        estado__in=estados_validos
    )
    
    # Usamos aggregate con filtros condicionales sobre las relaciones
    stats = pedidos.aggregate(
        webpay=Count('id', filter=Q(transacciones_webpay__estado='AUTORIZADO')),
        mercadopago=Count('id', filter=Q(transacciones_mercadopago__estado='approved')),
        transferencia=Count('id', filter=Q(pago_transferencia__estado='APROBADO'))
    )
    
    return {
        'webpay': stats['webpay'] or 0,
        'mercadopago': stats['mercadopago'] or 0,
        'transferencia': stats['transferencia'] or 0
    }

# =========================================
# VISTA PRINCIPAL DE MÉTRICAS
# =========================================

@admin_required
# @user_passes_test... (si usas este decorador también, mantenlo)
@admin_required
def ver_metricas(request):
    now = timezone.now()
    
    hace_una_semana = now - datetime.timedelta(days=7)
    hace_un_mes = now - datetime.timedelta(days=30)
    hace_un_ano = now - datetime.timedelta(days=365)
    inicio_de_los_tiempos = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    metrics_data = {
        'weekly': {
            'sales_over_time': obtener_ventas_en_tiempo(hace_una_semana, TruncDay),
            'shipping': obtener_metricas_envio(hace_una_semana),
            'payment': obtener_metricas_pago(hace_una_semana), # <--- NUEVO
            'top_products': obtener_top_productos(hace_una_semana)
        },
        'monthly': {
            'sales_over_time': obtener_ventas_en_tiempo(hace_un_mes, TruncDay),
            'shipping': obtener_metricas_envio(hace_un_mes),
            'payment': obtener_metricas_pago(hace_un_mes), # <--- NUEVO
            'top_products': obtener_top_productos(hace_un_mes)
        },
        'yearly': {
            'sales_over_time': obtener_ventas_en_tiempo(hace_un_ano, TruncMonth),
            'shipping': obtener_metricas_envio(hace_un_ano),
            'payment': obtener_metricas_pago(hace_un_ano), # <--- NUEVO
            'top_products': obtener_top_productos(hace_un_ano)
        },
        'all_time': {
            'sales_over_time': obtener_ventas_en_tiempo(inicio_de_los_tiempos, TruncYear),
            'shipping': obtener_metricas_envio(inicio_de_los_tiempos),
            'payment': obtener_metricas_pago(inicio_de_los_tiempos), # <--- NUEVO
            'top_products': obtener_top_productos(inicio_de_los_tiempos)
        }
    }

    return render(request, 'gestion/metrics.html', {'metrics_data': metrics_data})

def subir_comprobante(request, pedido_id):
    # 1. Obtenemos el pedido
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # 2. Validaciones de seguridad (para que no entren si no corresponde)
    if pedido.estado != 'procesando' and pedido.estado != 'pendiente': 
         messages.error(request, 'Este pedido no requiere subida de comprobantes actualmente.')
         return redirect('home')

    # 3. Verificar si ya subió algo antes (para no duplicar)
    # Nota: Si ya existe un pago PENDIENTE, asumimos que está esperando revisión.
    # Si quisieras permitir re-subir en caso de error, podrías quitar este bloque.
    if hasattr(pedido, 'pago_transferencia'):
        if pedido.pago_transferencia.estado == 'PENDIENTE' and request.method == 'GET':
             # Si es GET y ya tiene pago, mostramos la vista de "Ya enviado"
             return render(request, 'store/subir_comprobante.html', {
                 'pedido': pedido,
                 'upload_exitoso': True # Forzamos la vista de éxito
             })

    # 4. Procesar el formulario cuando se envía (POST)
    if request.method == 'POST':
        form = ComprobantePagoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # A. Crear el registro de PagoTransferencia
                    # Usamos get_or_create para evitar duplicados si el usuario refresca
                    pago_transferencia, created = PagoTransferencia.objects.get_or_create(
                        pedido=pedido,
                        defaults={
                            'comentario_usuario': form.cleaned_data['comentario'],
                            'estado': 'PENDIENTE'
                        }
                    )
                    
                    # B. Guardar las imágenes
                    imagenes = request.FILES.getlist('imagenes')
                    for imagen in imagenes:
                        ComprobanteTransferencia.objects.create(
                            pago=pago_transferencia,
                            imagen=imagen
                        )
                
                # === CORRECCIÓN CLAVE AQUÍ ===
                # En lugar de redirigir al PDF, nos quedamos aquí y mostramos éxito.
                context = {
                    'pedido': pedido,
                    'upload_exitoso': True  # Esta variable activa la pantalla de éxito
                }
                messages.success(request, '¡Comprobantes recibidos correctamente!')
                return render(request, 'store/subir_comprobante.html', context)
                # =============================

            except Exception as e:
                messages.error(request, f'Hubo un error al guardar tus comprobantes: {e}')
    else:
        form = ComprobantePagoForm()

    # 5. Datos para la vista normal (cuando aún no paga)
    cuentas_bancarias = [
        {
            'banco': 'Banco de Chile',
            'tipo_cuenta': 'Cuenta Corriente',
            'numero': '987654321',
            'nombre': 'TechTop SpA',
            'rut': '76.543.210-K',
            'correo': 'pagos@techtop.cl'
        },
        {
            'banco': 'Banco Santander',
            'tipo_cuenta': 'Cuenta Vista',
            'numero': '123456789',
            'nombre': 'TechTop SpA',
            'rut': '76.543.210-K',
            'correo': 'pagos@techtop.cl'
        }
    ]

    context = {
        'pedido': pedido,
        'form': form,
        'cuentas': cuentas_bancarias
    }
    return render(request, 'store/subir_comprobante.html', context)

# --- NUEVAS VISTAS PARA EL ADMINISTRADOR ---

@admin_required
def listar_transferencias_view(request):
    # Listar solo las pendientes primero, luego las revisadas
    transferencias = PagoTransferencia.objects.all().order_by(
        Case(When(estado='PENDIENTE', then=0), default=1),
        '-fecha_subida'
    )
    
    paginator = Paginator(transferencias, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gestion/transferencias_list.html', {'page_obj': page_obj})

@admin_required
def gestionar_transferencia_view(request, pago_id):
    pago = get_object_or_404(PagoTransferencia, id=pago_id)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'aprobar':
            pago.estado = 'APROBADO'
            pago.fecha_revision = timezone.now()
            pago.save()
            
            # Actualizar el pedido a 'procesando' (pagado)
            pago.pedido.estado = 'procesando'
            pago.pedido.save()
            
            enviar_recibo_por_email(pago.pedido)
            
            messages.success(request, f'Pago del pedido #{pago.pedido.id} APROBADO.')
            return redirect('listar_transferencias')
            
        elif accion == 'rechazar':
            pago.estado = 'RECHAZADO'
            pago.fecha_revision = timezone.now()
            pago.save()
            
            # Actualizar pedido a cancelado y devolver stock
            pedido = pago.pedido
            pedido.estado = 'cancelado'
            pedido.save()
            
            for detalle in pedido.detalles.all():
                producto = detalle.producto
                producto.stock += detalle.cantidad
                producto.save()
            
            messages.warning(request, f'Pago del pedido #{pedido.id} RECHAZADO. Stock restaurado.')
            return redirect('listar_transferencias')
    
    return render(request, 'gestion/transferencia_detail.html', {'pago': pago})


def cancelar_pedido_transferencia(request, pedido_id):
    """
    Permite al usuario cancelar un pedido pendiente de transferencia.
    Restaura el stock de los productos.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if pedido.estado not in ['procesando', 'pendiente']: 
        messages.error(request, 'No se puede cancelar este pedido.')
        return redirect('home')

    try:
        with transaction.atomic():
            for detalle in pedido.detalles.select_for_update():
                producto = detalle.producto
                producto.stock += detalle.cantidad
                if not producto.activo and producto.stock > 0:
                    producto.activo = True
                producto.save()

            pedido.estado = 'cancelado'
            pedido.save()

            if hasattr(pedido, 'pago_transferencia'):
                pedido.pago_transferencia.estado = 'RECHAZADO' 
                pedido.pago_transferencia.save()

        messages.info(request, 'El pedido ha sido cancelado correctamente.')

    except Exception as e:
        messages.error(request, 'Hubo un error al intentar cancelar el pedido.')

    return redirect('home') 

# --- Decorador mejorado para permitir Clientes Y Empleados ---
def usuario_logueado_required(view_func):
    """Decorador que permite acceso a Clientes y Empleados."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_type'):
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- Vistas de Perfil Adaptadas ---

@usuario_logueado_required
def perfil_usuario_view(request):
    user_type = request.session.get('user_type')
    
    if user_type == 'cliente':
        cliente = get_object_or_404(Cliente, id_cliente=request.session.get('cliente_id'))
        ultimas_compras = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')[:5]
        context = {'cliente': cliente, 'ultimas_compras': ultimas_compras, 'es_cliente': True}
    
    elif user_type == 'empleado':
        empleado = get_object_or_404(Empleado, id_empleado=request.session.get('empleado_id'))
        # Los empleados no suelen tener compras asociadas en este modelo, 
        # pero podríamos mostrar las últimas ventas generales si quisieras.
        # Por ahora, lo dejamos simple.
        context = {'cliente': empleado, 'es_cliente': False} # Usamos 'cliente' en el template para reutilizarlo
        
    return render(request, 'usuario/perfil.html', context)

@usuario_logueado_required
def editar_perfil_view(request):
    user_type = request.session.get('user_type')
    usuario = None
    direccion = None

    if user_type == 'cliente':
        usuario = get_object_or_404(Cliente, id_cliente=request.session.get('cliente_id'))
        direccion = Direccion.objects.filter(cliente=usuario).last()
    elif user_type == 'empleado':
        usuario = get_object_or_404(Empleado, id_empleado=request.session.get('empleado_id'))
        # Empleados no tienen dirección en este modelo por ahora

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST)
        if form.is_valid():
            # Actualizar datos comunes
            usuario.nombre = form.cleaned_data['nombre']
            usuario.apellidos = form.cleaned_data['apellidos']
            usuario.telefono = form.cleaned_data['telefono']
            usuario.save()
            
            # Solo actualizar dirección si es cliente
            if user_type == 'cliente' and form.cleaned_data['calle']:
                if not direccion:
                    direccion = Direccion(cliente=usuario)
                direccion.calle = form.cleaned_data['calle']
                direccion.ciudad = form.cleaned_data.get('ciudad', '')
                direccion.region = form.cleaned_data.get('region', '')
                direccion.save()
                
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil_usuario')
    else:
        initial_data = {
            'nombre': usuario.nombre,
            'apellidos': usuario.apellidos,
            'email': usuario.email,
            'telefono': usuario.telefono,
        }
        if user_type == 'cliente' and direccion:
            initial_data.update({
                'calle': direccion.calle,
                'ciudad': direccion.ciudad,
                'region': direccion.region,
            })
        form = PerfilUsuarioForm(initial=initial_data)

    return render(request, 'usuario/editar_perfil.html', {'form': form, 'es_cliente': (user_type == 'cliente')})

@usuario_logueado_required
def historial_compras_view(request):
    user_type = request.session.get('user_type')
    
    if user_type == 'empleado':
        # Opcional: Permitir que el admin vea TODAS las compras aquí, o redirigirlo.
        # Por ahora, redirigimos al panel de gestión que es más apropiado para ellos.
        messages.info(request, 'Como administrador, puedes ver todas las transacciones en el Panel de Gestión.')
        return redirect('panel_gestion')

    cliente = get_object_or_404(Cliente, id_cliente=request.session.get('cliente_id'))
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
    
    paginator = Paginator(pedidos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'usuario/historial_compras.html', {'page_obj': page_obj})

@usuario_logueado_required
def detalle_compra_view(request, pedido_id):
    user_type = request.session.get('user_type')
    
    if user_type == 'empleado':
         # Permitir al admin ver cualquier pedido
         pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
         # Cliente solo ve SUS pedidos
         cliente_id = request.session.get('cliente_id')
         pedido = get_object_or_404(Pedido, id=pedido_id, cliente__id_cliente=cliente_id)
    
    return render(request, 'usuario/detalle_compra.html', {'pedido': pedido})

# En store/views.py

@admin_required
def listar_pedidos_view(request):
    # Filtrado inicial base
    pedidos = Pedido.objects.all().order_by('-fecha_pedido').select_related('cliente', 'direccion_envio')

    # --- FILTROS ---
    # 1. Filtro por Tipo de Entrega
    delivery_filter = request.GET.get('entrega')
    if delivery_filter == 'delivery':
        pedidos = pedidos.filter(direccion_envio__isnull=False)
    elif delivery_filter == 'retiro':
        pedidos = pedidos.filter(direccion_envio__isnull=True)

    # 2. Filtro por Método de Pago
    pago_filter = request.GET.get('pago')
    if pago_filter in ['webpay', 'mercadopago', 'transferencia']:
        pedidos = pedidos.filter(metodo_pago=pago_filter)

    # 3. Filtro por Estado
    estado_filter = request.GET.get('estado')
    if estado_filter:
        pedidos = pedidos.filter(estado=estado_filter)

    # Paginación
    paginator = Paginator(pedidos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gestion/pedidos_list.html', {
        'page_obj': page_obj,
        # Pasamos los filtros actuales al template para mantenerlos seleccionados
        'current_entrega': delivery_filter,
        'current_pago': pago_filter,
        'current_estado': estado_filter
    })

@admin_required
def gestionar_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        
        if nuevo_estado and nuevo_estado != pedido.estado:
            estado_anterior = pedido.get_estado_display()
            pedido.estado = nuevo_estado
            pedido.save()
            
            # --- CREAR NOTIFICACIÓN AUTOMÁTICA ---
            if pedido.cliente:
                Notificacion.objects.create(
                    cliente=pedido.cliente,
                    pedido=pedido,
                    mensaje=f"El estado de tu pedido #{pedido.id} ha cambiado a: {pedido.get_estado_display()}"
                )
            
            messages.success(request, f'Pedido #{pedido.id} actualizado a {pedido.get_estado_display()}. Notificación enviada al cliente.')
            return redirect('gestionar_pedido', pedido_id=pedido.id)

    return render(request, 'gestion/pedido_detail.html', {'pedido': pedido})


@usuario_logueado_required
def mis_notificaciones_view(request):
    user_type = request.session.get('user_type')
    if user_type != 'cliente':
        # Si no es cliente, no tiene notificaciones de pedido por ahora
        # Podrías redirigir al perfil o mostrar una lista vacía
        return render(request, 'usuario/notificaciones.html', {'notificaciones': []})

    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cliente, id_cliente=cliente_id)
    
    # Obtener todas las notificaciones
    notificaciones = cliente.notificaciones.all()
    
    # Marcar todas como leídas al entrar a la vista
    cliente.notificaciones.filter(leida=False).update(leida=True)
    
    return render(request, 'usuario/notificaciones.html', {'notificaciones': notificaciones})

@admin_required
def listar_comentarios_view(request):
    """Muestra todos los comentarios, priorizando los pendientes."""
    comentarios_list = Comentario.objects.all().order_by('aprobado', '-fecha')
    
    # Filtro (opcional, pero útil)
    filtro = request.GET.get('filtro', 'pendientes')
    if filtro == 'pendientes':
        comentarios_list = comentarios_list.filter(aprobado=False)
    elif filtro == 'aprobados':
        comentarios_list = comentarios_list.filter(aprobado=True)
    
    paginator = Paginator(comentarios_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gestion/comentarios_list.html', {
        'page_obj': page_obj,
        'filtro_actual': filtro
    })

@admin_required
@require_http_methods(["POST"])
def aprobar_comentario_view(request, comentario_id):
    """Aprueba un comentario para que sea público."""
    comentario = get_object_or_404(Comentario, id=comentario_id)
    comentario.aprobado = True
    comentario.save()
    messages.success(request, f'Comentario #{comentario.id} aprobado exitosamente.')
    return redirect('listar_comentarios')

@admin_required
@require_http_methods(["POST"])
def rechazar_comentario_view(request, comentario_id):
    """Rechaza (elimina) un comentario."""
    comentario = get_object_or_404(Comentario, id=comentario_id)
    comentario.delete()
    messages.warning(request, f'Comentario #{comentario.id} eliminado/rechazado exitosamente.')
    return redirect('listar_comentarios')


# En store/views.py

def seguimiento_compra(request):
    pedido_encontrado = None
    error_mensaje = None
    orden_buscada = request.GET.get('orden_id', '').strip().upper() # Convertimos a mayúsculas

    if orden_buscada: 
        try:
            # --- CAMBIO AQUÍ: Buscamos por tracking_number ---
            pedido_encontrado = Pedido.objects.get(tracking_number=orden_buscada)
        except Pedido.DoesNotExist:
             error_mensaje = f"No encontramos ningún pedido con el número de seguimiento #{orden_buscada}."

    return render(request, 'seguimiento_compra.html', {
        'pedido': pedido_encontrado,
        'error': error_mensaje,
        'orden_buscada': orden_buscada
    })
    
# ==================== CHATBOT INTELIGENTE V3 (FINAL) ====================

def normalizar_texto(texto):
    """
    Normaliza el texto: elimina diacríticos (tildes, ñ->n) y convierte a minúsculas.
    Es vital que las palabras clave en los IFs también estén normalizadas.
    """
    if not texto: return ""
    # NFD separa caracteres base de sus modificadores (ej: ñ -> n + ~)
    # Luego filtramos los modificadores (Mn)
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower().strip()

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_view(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        response = generate_chatbot_response(user_message)
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'message': 'Lo siento, tuve un error interno.', 'data': None}, status=500)

def generate_chatbot_response(message_raw):
    # 1. Normalización (IMPORTANTE: 'dañado' se convierte en 'danado')
    msg = normalizar_texto(message_raw)
    words = set(msg.split()) # Set para búsqueda rápida de palabras exactas

    # ================================================================
    # NIVEL 1: SOPORTE URGENTE (Envíos, Daños)
    # ================================================================

    # CASO: Producto dañado o fallas
    # Keywords normalizadas: 'danado' en lugar de 'dañado'
    if any(w in msg for w in ['roto', 'danado', 'malo', 'falla', 'no funciona', 'defectuoso', 'quebrado', 'golpeado', 'llego mal']):
        return {
            'message': '😟 <strong>¿Tu producto llegó con problemas?</strong><br><br>Lo lamentamos mucho. Por favor, ingresa a nuestro Centro de Ayuda para gestionar una solución rápida (cambio o devolución).<br><br>👉 <a href="/centro-ayuda/" style="color: #667eea; font-weight: bold;">Ir al Centro de Ayuda</a>',
            'data': {'type': 'link', 'url': '/centro-ayuda/'}
        }

    # CASO: Problemas de envío / No llega
    # Detecta combinaciones como "no llega", "aun no recibo", "retraso"
    if ('no' in words and any(w in msg for w in ['llega', 'recib', 'llegado'])) or \
       any(w in msg for w in ['retraso', 'demora', 'tarda', 'donde viene']):
        return {
            'message': '🚚 <strong>¿Tu pedido está demorado?</strong><br><br>Revisa el estado actual aquí:<br><br>👉 <a href="/seguimiento-compra/" style="color: #667eea; font-weight: bold;">Seguimiento de Compra</a><br><br>Si el plazo expiró, contáctanos de inmediato.',
            'data': {'type': 'link', 'url': '/seguimiento-compra/'}
        }

    # CASO: Seguimiento general (sin queja)
    if any(w in msg for w in ['seguimiento', 'rastrea', 'donde esta mi', 'estado del pedido']):
         return {
            'message': '📦 <strong>Rastrea tu pedido</strong><br><br>Puedes ver la ubicación de tu compra ingresando tu número de orden aquí:<br><br>👉 <a href="/seguimiento-compra/" style="color: #667eea; font-weight: bold;">Ir a Seguimiento</a>',
            'data': {'type': 'link', 'url': '/seguimiento-compra/'}
        }
         
# CASO: Ofertas (MODIFICADO)
    if any(w in msg for w in ['oferta', 'ofertas', 'descuento', 'barato', 'economico', 'liquidacion']):
        
        # 1. [NUEVO] Buscamos productos que tengan un descuento (slider) aplicado.
        productos_en_oferta = Producto.objects.filter(
            activo=True, 
            stock__gt=0, 
            descuento__gt=0  # <-- La nueva condición clave
        ).order_by('?')[:5] # <-- Pide 5 aleatorios directamente

        # 2. Si encontramos productos en oferta, los mostramos
        if productos_en_oferta.exists():
            return crear_respuesta_productos(productos_en_oferta, "🔥 ¡Nuestras Ofertas Especiales!")
        else:
            # 3. [NUEVO FALLBACK] Si NO hay ofertas, mostramos 5 productos aleatorios
            productos_aleatorios = Producto.objects.filter(activo=True, stock__gt=0).order_by('?')[:5]
            if productos_aleatorios.exists():
                return crear_respuesta_productos(productos_aleatorios, "🤔 No hay ofertas especiales activas ahora mismo, ¡pero mira estos productos!")
            else:
                # Si no hay nada, mensaje de stock
                return {
                    'message': 'Lo sentimos, no encontramos productos disponibles en este momento.',
                    'data': None
                }

    # CASO: Tiempos de envío / Plazos
    # Detecta preguntas sobre cuánto demora el envío general (no un pedido específico)
    if any(w in msg for w in ['tiempo', 'plazo', 'demora', 'tarda', 'dias']) and any(w in msg for w in ['envio', 'despacho', 'entrega', 'llegar']):
        return {
            'message': '🚚 <strong>Plazos de Envío Aproximados</strong><br><br>• <strong>Santiago:</strong> 24 a 48 horas hábiles.<br>• <strong>Regiones:</strong> 2 a 5 días hábiles (depende de la zona).<br><br>Recibirás un código de seguimiento apenas tu compra sea despachada.',
            'data': {'type': 'info'}
        }

    # CASO: Garantías (Información general)
    if any(w in msg for w in ['garantia', 'devolucion', 'cambio', 'falla']):
         return {
            'message': '🛡️ <strong>Políticas de Garantía</strong><br><br>✅ <strong>Garantía Legal (6 meses):</strong> Cubre fallas de fabricación.<br>✅ <strong>Satisfacción (10 días):</strong> Devolución si el producto no cumple tus expectativas (debe estar sellado/nuevo).<br><br>👉 <a href="/garantias/" style="color: #667eea; font-weight: bold;">Ver Política Completa</a>',
            'data': {'type': 'link', 'url': '/garantias/'}
        }

    # CASO: Pago en cuotas (Complemento a medios de pago)
    if 'cuotas' in msg:
         return {
             'message': '💳 <strong>Pago en Cuotas</strong><br><br>¡Sí! Puedes pagar en cuotas usando tarjetas de crédito a través de <strong>Webpay Plus</strong> o <strong>Mercado Pago</strong>.<br><br>ℹ️ <em>La cantidad de cuotas sin interés dependerá de las promociones vigentes con tu banco.</em>',
             'data': {'type': 'info'}
         }

    # CASO: Centro de Ayuda (Preguntas frecuentes)
    if any(w in msg for w in ['ayuda', 'faq', 'preguntas', 'dudas']):
        return {
            'message': '❓ <strong>Centro de Ayuda</strong><br><br>Encuentra respuestas rápidas a las consultas más comunes en nuestra sección de ayuda:<br><br>👉 <a href="/centro-ayuda/" style="color: #667eea; font-weight: bold;">Ir a Preguntas Frecuentes</a>',
            'data': {'type': 'link', 'url': '/centro-ayuda/'}
        }

    # ================================================================
    # NIVEL 2: INFORMACIÓN GENERAL Y CONTACTO
    # ================================================================

    # CASO: Contacto (Solicitado explícitamente)
    if any(w in msg for w in ['humano', 'persona', 'agente', 'ejecutivo', 'alguien real', 'asesor']):
        return {
            'message': '🤖 <strong>¿Prefieres atención personalizada?</strong><br><br>Entiendo, a veces es mejor hablar con una persona. Nuestro equipo humano está disponible en:<br><br>📱 <strong>WhatsApp:</strong> +56 9 6652 6672<br>📞 <strong>Teléfono:</strong> (mismo número)<br>📧 <strong>Email:</strong> contacto@techtop.cl<br>⏰ <strong>Horario:</strong> Lun-Vie 09:00 - 18:00 hrs',
            'data': {'type': 'info'}
        }
        
    if any(w in msg for w in ['contacto', 'contactar', 'telefono', 'celular', 'correo', 'email', 'hablar con alguien', 'direccion', 'ubicacion', 'donde estan']):
        return {
            'message': '📞 <strong>Canales de Contacto TechTop</strong><br><br>• 📱 <strong>Teléfono/WhatsApp:</strong> +56 9 6652 6672<br>• 📧 <strong>Email:</strong> contacto@techtop.cl<br>• 📍 <strong>Ubicación:</strong> Santiago, Región Metropolitana<br><br>También puedes usar nuestro formulario web:<br><br>👉 <a href="/contacto/" style="color: #667eea; font-weight: bold;">Ir a Página de Contacto</a>',
            'data': {'type': 'link', 'url': '/contacto/'} # Redirige o muestra botón si el JS lo soporta
        }

    # CASO: Métodos de pago
    if any(w in msg for w in ['pago', 'pagar', 'tarjeta', 'cuotas', 'transferencia', 'redcompra']):
        return {
            'message': '💳 <strong>Medios de Pago Aceptados</strong><br><br>✅ <strong>Webpay Plus:</strong> Tarjetas de crédito y débito.<br>✅ <strong>Mercado Pago:</strong> Saldo en cuenta y tarjetas guardadas.<br>✅ <strong>Transferencia:</strong> ¡Obtén un <strong>3% de DESCUENTO</strong> pagando así!',
            'data': {'type': 'info'}
        }

    # ================================================================
    # NIVEL 3: BÚSQUEDA DE PRODUCTOS
    # ================================================================

    # CASO: "Ver productos" genérico -> Muestra RANDOM
    # Si el mensaje es muy corto y genérico, mostramos variedad.
    if msg in ['ver productos', 'productos', 'quiero ver productos', 'muestrame productos', 'tienda', 'catalogo']:
        # .order_by('?') obtiene registros aleatorios
        productos = Producto.objects.filter(activo=True, stock__gt=0).order_by('?')[:6]
        return crear_respuesta_productos(productos, "Explora nuestro catálogo 🚀")

    # CASO: Búsqueda específica (Marcas, Categorías, Palabras clave)
    # Usamos la misma lógica de detección combinada de la V2 mejorada, 
    # pero aseguramos que busque por relevancia (fecha o precio) si es específico.
    
    # 1. Detectar marcas y categorías en el mensaje
    marcas_detectadas = [m for m in Marca.objects.all() if normalizar_texto(m.nombre) in msg]
    cats_detectadas = [c for c in Categoria.objects.all() if normalizar_texto(c.nombre) in msg]

    if marcas_detectadas and cats_detectadas:
        # Búsqueda combinada: "Radio Kia"
        prods = Producto.objects.filter(marca=marcas_detectadas[0], categoria=cats_detectadas[0], activo=True, stock__gt=0)[:6]
        if prods.exists(): return crear_respuesta_productos(prods, f"{cats_detectadas[0].nombre} para {marcas_detectadas[0].nombre}")

    if marcas_detectadas:
        # Solo marca: "Cosas para Toyota" -> mostrar lo más nuevo
        prods = Producto.objects.filter(marca=marcas_detectadas[0], activo=True, stock__gt=0).order_by('-fecha_pub')[:6]
        return crear_respuesta_productos(prods, f"Productos {marcas_detectadas[0].nombre}")

    if cats_detectadas:
        # Solo categoría: "Muestrame radios" -> mostrar aleatorios de esa categoría para variedad
        prods = Producto.objects.filter(categoria=cats_detectadas[0], activo=True, stock__gt=0).order_by('?')[:6]
        return crear_respuesta_productos(prods, f"Categoría: {cats_detectadas[0].nombre}")

    # 2. Búsqueda por palabras clave (último recurso de búsqueda)
    intentos_busqueda = ['busco', 'quiero', 'necesito', 'tienes', 'venden', 'precio', 'valor', 'mostrar', 'ver']
    if any(i in msg for i in intentos_busqueda) or len(words) > 1: # Si parece una búsqueda
        palabras_clave = [w for w in words if len(w) > 3 and w not in intentos_busqueda]
        if palabras_clave:
            query = Q()
            for p in palabras_clave:
                query |= Q(nombre__icontains=p) | Q(descripcion__icontains=p)
            prods = Producto.objects.filter(query, activo=True, stock__gt=0).order_by('?')[:6]
            if prods.exists():
                return crear_respuesta_productos(prods, "Lo que encontré para ti")

    # ================================================================
    # NIVEL 4: SALUDOS Y DESPEDIDAS
    # ================================================================
    if any(w in words for w in ['hola', 'buenas', 'alo', 'hey']):
        return {'message': '¡Hola! 👋 Bienvenido a TechTop. ¿En qué te puedo ayudar hoy? (Puedes pedirme ver productos, seguimiento de pedidos o contacto)', 'data': {'type': 'welcome'}}

    if any(w in words for w in ['gracias', 'chao', 'adios']):
        return {'message': '¡De nada! 😊 Estamos para ayudarte.', 'data': None}

    # RESPUESTA POR DEFECTO
    return {
        'message': '🤔 No entendí bien tu consulta. Prueba con:<br><br>• "Ver productos" (para ver variedad)<br>• "Radio para Nissan"<br>• "Seguimiento de pedido"<br>• "Contacto"',
        'data': None
    }

def crear_respuesta_productos(productos, titulo):
    """
    Genera el HTML de las tarjetas de producto CON PRECIOS DE OFERTA.
    """
    html = f'🎯 <strong>{titulo}:</strong><div class="chatbot-products-grid">'
    
    for p in productos:
        img_url = p.imagen.url if p.imagen else '/static/img/no-image.png'
        
        # Obtenemos los precios correctos desde las propiedades del modelo
        precio_oferta_val = p.precio_oferta
        precio_transf_val = p.precio_transferencia
        precio_original_val = int(p.precio)

        # --- Construcción del HTML de precios ---
        price_html = ""
        
        # 1. Si hay descuento (slider > 0), mostramos el precio original tachado
        if p.descuento > 0:
            price_html += f'''
            <p class="price-original" style="text-decoration: line-through; color: #999; font-size: 0.8rem; margin: 0;">
                ${precio_original_val:,.0f}
            </p>
            '''

        # 2. Mostramos el precio de oferta (para Webpay/Otros)
        price_html += f'''
        <p class="price" style="font-weight: bold; color: #333; margin: 0;">
            ${precio_oferta_val:,.0f}
        </p>
        '''

        # 3. Mostramos el precio de transferencia (Oferta + 3% extra)
        price_html += f'''
        <p class="price-transfer" style="font-weight: normal; color: #444; font-size: 0.9rem;">
            ⚡ ${precio_transf_val:,.0f} (Transferencia)
        </p>
        '''
        
        # --- Fin construcción HTML ---

        html += f'''
        <div class="chatbot-product-card" onclick="window.location.href='/producto/{p.id}/'">
            <img src="{img_url}">
            <div class="chatbot-product-info">
                <h4>{p.nombre}</h4>
                {price_html}
            </div>
        </div>'''
    
    html += '</div>'
    return {'message': html, 'data': {'type': 'productos'}}

def password_reset_request(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'GET':
        return render(request, 'password_reset_request.html')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Validar email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Por favor, ingresa un correo electrónico válido.')
            return redirect('password_reset_request')
        
        # Buscar cliente
        try:
            cliente = Cliente.objects.get(email=email)
            
            # Invalidar tokens anteriores
            PasswordResetToken.objects.filter(cliente=cliente, usado=False).update(usado=True)
            
            # Crear nuevo token
            token = PasswordResetToken.objects.create(
                cliente=cliente,
                token=PasswordResetToken.generate_token()
            )
            
            # Crear URL de recuperación
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token': token.token})
            )
            
            # Enviar email
            try:
                send_mail(
                    subject='Recuperación de Contraseña - Techtop',
                    message=f'''Hola {cliente.nombre},

Recibimos una solicitud para restablecer tu contraseña en Techtop.

Para crear una nueva contraseña, haz clic en el siguiente enlace (válido por 1 hora):
{reset_url}

Si no solicitaste este cambio, ignora este correo. Tu contraseña actual seguirá siendo válida.

Saludos,
Equipo Techtop''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[cliente.email],
                    fail_silently=False,
                )
                
                messages.success(request, f'Se ha enviado un enlace de recuperación a {email}. Revisa tu bandeja de entrada.')
            except Exception as e:
                messages.error(request, 'Hubo un error al enviar el correo. Por favor, intenta nuevamente.')
                return redirect('password_reset_request')
                
        except Cliente.DoesNotExist:
            # Por seguridad, mostramos el mismo mensaje aunque no exista
            messages.success(request, f'Si existe una cuenta con {email}, recibirás un enlace de recuperación.')
        
        return redirect('login')


def password_reset_confirm(request, token):
    """Vista para confirmar y establecer nueva contraseña"""
    # Buscar token
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'El enlace de recuperación no es válido.')
        return redirect('login')
    
    # Verificar validez
    if not reset_token.is_valid():
        messages.error(request, 'El enlace de recuperación ha expirado. Solicita uno nuevo.')
        return redirect('password_reset_request')
    
    if request.method == 'GET':
        return render(request, 'password_reset_confirm.html', {'token': token})
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        # Validar contraseñas
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        # Validar seguridad de contraseña
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        if not re.search(r'[a-z]', password):
            messages.error(request, 'La contraseña debe contener al menos una letra minúscula.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        if not re.search(r'[A-Z]', password):
            messages.error(request, 'La contraseña debe contener al menos una letra mayúscula.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        if not re.search(r'\d', password):
            messages.error(request, 'La contraseña debe contener al menos un número.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?~`]', password):
            messages.error(request, 'La contraseña debe contener al menos un carácter especial.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
        # Actualizar contraseña
        try:
            cliente = reset_token.cliente
            cliente.pass_hash = make_password(password)
            cliente.save()
            
            # Marcar token como usado
            reset_token.usado = True
            reset_token.save()
            
            messages.success(request, '¡Tu contraseña ha sido actualizada exitosamente! Ya puedes iniciar sesión.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, 'Hubo un error al actualizar tu contraseña. Intenta nuevamente.')
            return render(request, 'password_reset_confirm.html', {'token': token})
        
def enviar_recibo_por_email(pedido):
    """
    Genera un PDF del recibo y lo envía por email al cliente.
    Retorna True si se envió exitosamente, False si hubo un error.
    """
    try:
        # Obtener datos del pedido
        detalles = pedido.detalles.select_related('producto').all()
        
        # Datos del cliente
        cliente_nombre_completo = 'Cliente no registrado'
        cliente_email = None
        cliente_rut = 'No disponible'
        
        if pedido.cliente:
            cliente_nombre_completo = f"{pedido.cliente.nombre} {pedido.cliente.apellidos}"
            cliente_email = pedido.cliente.email
            cliente_rut = getattr(pedido.cliente, 'rut', 'No disponible')
        
        # Si no hay email, no podemos enviar
        if not cliente_email:
            return False
        
        # Cálculos
        subtotal = sum(d.precio_unitario * d.cantidad for d in detalles)
        total_iva = subtotal * Decimal('0.19')
        costo_envio = Decimal('4500') if pedido.direccion_envio else Decimal('0.00')
        total_pagado = pedido.total
        
        logo_path = f"{settings.STATIC_URL}img/new_black.png"
        
        # Contexto para el template
        context = {
            'pedido': pedido,
            'detalles': detalles,
            'cliente_nombre_completo': cliente_nombre_completo,
            'cliente_email': cliente_email,
            'cliente_rut': cliente_rut,
            'subtotal': subtotal,
            'total_iva': total_iva,
            'costo_envio': costo_envio,
            'total_pagado': total_pagado,
            'logo_path': logo_path,
            'fecha_actual': timezone.now()
        }
        
        # Generar HTML del PDF
        template = get_template('store/recibo_pdf.html')
        html = template.render(context)
        
        # Crear PDF en memoria
        result = BytesIO()
        pdf = pisa.CreatePDF(html, dest=result)
        
        if pdf.err:
            return False
        
        # Obtener el contenido del PDF
        pdf_content = result.getvalue()
        
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        seguimiento_url = f"{site_url}/seguimiento-compra/"
        
        # Crear el email
        email = EmailMessage(
            subject=f'Comprobante de Compra - Pedido #{pedido.id} - Techtop',
            body=f'''Hola {cliente_nombre_completo},

¡Gracias por tu compra en Techtop!

Adjunto encontrarás el comprobante de tu pedido #{pedido.id}.

Número de Seguimiento: {pedido.tracking_number}

Puedes seguir el estado de tu pedido ingresando a:
{seguimiento_url}

Si tienes alguna consulta, no dudes en contactarnos.

Saludos,
Equipo Techtop
_______________________________________________
Este es un correo automático, por favor no responder.
Techtop - Tu tienda de tecnología de confianza
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[cliente_email],
        )
        
        # Adjuntar el PDF
        email.attach(
            filename=f'recibo_techtop_{pedido.tracking_number}.pdf',
            content=pdf_content,
            mimetype='application/pdf'
        )
        
        # Enviar el email
        email.send(fail_silently=False)
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False
    
# store/views.py

# Agregar estos imports al inicio si no los tienes
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import MensajeContacto

def contacto(request):
    if request.method == 'POST':
        # 1. Capturar datos y limpiar espacios (strip)
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()

        # --- INICIO VALIDACIONES ---

        # A. Validar campos vacíos
        if not all([nombre, apellido, email, mensaje]):
            messages.error(request, 'Por favor, completa todos los campos.')
            return render(request, 'contacto.html', {'nombre': nombre, 'apellido': apellido, 'email': email, 'mensaje': mensaje})

        # B. Validar Nombre (Solo letras y espacios, máx 50 caracteres)
        # Regex permite letras mayúsculas, minúsculas, tildes y ñ
        name_regex = r'^[a-zA-ZÀ-ÿ\u00f1\u00d1\s]+$'
        
        if len(nombre) > 50:
            messages.error(request, 'El nombre no puede tener más de 50 caracteres.')
            return render(request, 'contacto.html', {'nombre': nombre, 'apellido': apellido, 'email': email, 'mensaje': mensaje})
            
        if not re.match(name_regex, nombre):
            messages.error(request, 'El nombre solo debe contener letras.')
            return render(request, 'contacto.html', {'nombre': nombre, 'apellido': apellido, 'email': email, 'mensaje': mensaje})

        # C. Validar Apellido (Igual que nombre)
        if len(apellido) > 50:
            messages.error(request, 'El apellido no puede tener más de 50 caracteres.')
            return render(request, 'contacto.html', {'nombre': nombre, 'apellido': apellido, 'email': email, 'mensaje': mensaje})

        if not re.match(name_regex, apellido):
            messages.error(request, 'El apellido solo debe contener letras.')
            return render(request, 'contacto.html', {'nombre': nombre, 'apellido': apellido, 'email': email, 'mensaje': mensaje})

        # D. Validar Email (Formato correcto)
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Por favor, ingresa un correo electrónico válido.')
            return render(request, 'contacto.html', {'nombre': nombre, 'apellido': apellido, 'email': email, 'mensaje': mensaje})

        # --- FIN VALIDACIONES ---

        try:
            # Guardar (esto dispara el Signal que envía a n8n)
            MensajeContacto.objects.create(
                nombre=nombre,
                apellido=apellido,
                email=email,
                mensaje=mensaje
            )
            
            # Mensaje de éxito específico para que lo detecte SweetAlert
            messages.success(request, 'Su solicitud de contacto fue enviada correctamente')
            
            # Redirigir para limpiar el formulario (patrón PRG)
            return redirect('contacto')
            
        except Exception as e:
            print(f"Error guardando contacto: {e}")
            messages.error(request, 'Ocurrió un error interno. Intenta nuevamente.')

    return render(request, 'contacto.html')