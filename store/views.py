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


from .models import Producto, Marca, Categoria, Cliente, Empleado, Pedido, DetallePedido, Direccion, TransaccionWebpay, TransaccionMercadoPago, Comentario, PasswordResetToken
from .decorators import admin_required, superadmin_required
from .forms import CategoriaForm, MarcaForm, ProductoForm, CheckoutForm, EmpleadoForm
from .validators import validate_chilean_rut
from .models import MensajeContacto


@superadmin_required
def gestion_empleados(request):
    """
    Lista todos los empleados para que el superadmin los gestione.
    """
    empleados_list = Empleado.objects.all().order_by('apellidos', 'nombre')
    
    paginator = Paginator(empleados_list, 10) 
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
            form.save() 
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
    
    
    if empleado.id_empleado == request.session.get('empleado_id'):
        return JsonResponse({'success': False, 'message': 'No puedes desactivar tu propia cuenta.'}, status=403)

    empleado.activo = False
    empleado.save()
    
    return JsonResponse({'success': True, 'message': f'Empleado "{empleado.nombre} {empleado.apellidos}" ha sido desactivado.'})


def home(request):
    return render(request, 'home.html')

def contacto(request):
    return render(request, 'contacto.html')

def about(request):
    return render(request, 'about.html')

def seguimiento_compra(request):
    return render(request, 'seguimiento_compra.html')

def centro_ayuda(request):
    return render(request, 'centro_ayuda.html')

def garantias(request):
    return render(request, 'garantias.html')

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
    context = {
        'products': products,
        'available_brands': available_brands,
        'available_inches': available_inches,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'selected_inches_from_form': selected_inches,
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

    context = {
        'products': products,
        'categoria_actual': categoria,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': category_type,
        'parent_category': parent_category
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


    context = {
        'products': products,
        'available_brands': available_brands,
        'available_categories': available_categories,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'selected_categories_from_form': selected_categories,
        'category_type': 'electronica'
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


    context = {
        'products': products,
        'available_brands': available_brands,
        'available_categories': available_categories,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'selected_categories_from_form': selected_categories,
        'category_type': 'accesorios'
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

    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
        'selected_prices_from_form': selected_prices,
        'category_type': 'otros'
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

    
    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brand': brand_name,
        'selected_brands_from_form': selected_brands,
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
    product = get_object_or_404(Producto, id=product_id)
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
                request.session['is_superadmin'] = empleado.is_superadmin  
                
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

        
        
        
        if not all([rut, nombre, apellido, correo, telefono, password, password2]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        
        try:
            validate_chilean_rut(rut)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('register')

        
        if Cliente.objects.filter(rut=rut).exists():
            messages.error(request, 'El RUT ya está registrado en el sistema.')
            return redirect('register')

        
        name_regex = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(name_regex, nombre):
            messages.error(request, 'El nombre solo debe contener letras y espacios.')
            return redirect('register')
        
        if not re.match(name_regex, apellido):
            messages.error(request, 'El apellido solo debe contener letras y espacios.')
            return redirect('register')

        
        if len(nombre) < 2 or len(nombre) > 50:
            messages.error(request, 'El nombre debe tener entre 2 y 50 caracteres.')
            return redirect('register')
        
        if len(apellido) < 2 or len(apellido) > 100:
            messages.error(request, 'El apellido debe tener entre 2 y 100 caracteres.')
            return redirect('register')

        
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'Formato de correo electrónico inválido.')
            return redirect('register')

        
        if len(correo) > 100:
            messages.error(request, 'El correo electrónico es demasiado largo.')
            return redirect('register')

        
        if Cliente.objects.filter(email=correo).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return redirect('register')

        
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        
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
        
        request.session.pop('empleado_id', None)
        request.session.pop('empleado_nombre', None)
        request.session.pop('empleado_cargo', None)
        request.session.pop('cliente_id', None)
        request.session.pop('cliente_nombre', None)
        request.session.pop('user_type', None)
        
        
        logout(request)
        
        
        request.session.modified = True
        
        messages.success(request, '¡Has cerrado sesión exitosamente!')
        
        
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
        
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            
            publicar_redes = form.cleaned_data.get('publicar_redes', False)
            
            
            producto = form.save(commit=False)
            
            
            producto._publicar_redes = publicar_redes
            
            
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
    
    
    paginator = Paginator(productos_list, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gestion/productos_list.html', {'page_obj': page_obj})



@admin_required
def editar_producto_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        
        
        if form.is_valid():
            form.save() 
            messages.success(request, f'¡Producto "{producto.nombre}" actualizado exitosamente!')
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'gestion/editar_form.html', { 
        'form': form,
        'titulo': f'Editar Producto: {producto.nombre}',
        'objeto_id': producto.id,
        'volver_url': 'listar_productos'
    })


def eliminar_producto_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        
        return JsonResponse({'success': True, 'message': f'Producto "{nombre_producto}" eliminado exitosamente.'})
    
    return JsonResponse({'success': False, 'message': 'Petición no válida.'})




def listar_categorias_view(request):
    categorias_list = Categoria.objects.all().order_by('id')
    paginator = Paginator(categorias_list, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gestion/categorias_list.html', {'page_obj': page_obj})



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


def eliminar_categoria_view(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre_categoria = categoria.nombre
        categoria.delete()
        return JsonResponse({'success': True, 'message': f'Categoría "{nombre_categoria}" eliminada exitosamente.'})
    return JsonResponse({'success': False, 'message': 'Petición no válida.'})




def listar_marcas_view(request):
    marcas_list = Marca.objects.all().order_by('id')
    paginator = Paginator(marcas_list, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gestion/marcas_list.html', {'page_obj': page_obj})



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
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="productos_techtop.csv"'},
    )
    
    response.write(u'\ufeff'.encode('utf8'))

    
    writer = csv.writer(response)

    
    writer.writerow(['ID', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría', 'Marca'])

    
    
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

    
    return response

def exportar_categorias_csv(request):
    """
    Genera un archivo CSV con todas las categorías.
    """
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="categorias_techtop.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8')) 

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Descripción'])

    for categoria in Categoria.objects.all():
        writer.writerow([categoria.id, categoria.nombre, categoria.descripcion])

    return response


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
    
    products = Producto.objects.filter(categoria__nombre='Audio-y-Video')
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
    
    products = Producto.objects.filter(categoria__nombre='Seguridad-y-Sensores')
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
    
    products = Producto.objects.filter(categoria__nombre='Diagnostico-Automotriz')
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
    
    products = Producto.objects.filter(categoria__nombre='Herramientas-de-Medicion')
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
    
    products = Producto.objects.filter(categoria__nombre='Medidores')
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
    
    products = Producto.objects.filter(categoria__nombre='Electronica-Automotriz')
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
    
    products = Producto.objects.filter(categoria__nombre='Electronica-General')
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

    context = {
        'products': products,
        'search_query': query,
    }
    return render(request, 'store/search_results.html', context)




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

        
        product_ids = cart.keys()
        
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

        
        cliente_obj = None
        if request.session.get('user_type') == 'cliente':
            try:
                cliente_obj = Cliente.objects.get(id_cliente=request.session.get('cliente_id'))
            except Cliente.DoesNotExist:
                pass 

        
        direccion_obj = None
        costo_envio_calculado = Decimal('0')
        
        if tipo_entrega == 'delivery':
            costo_envio_calculado = Decimal('4500') 
            
            if cliente_obj:
                 try:
                     
                     direccion_obj = Direccion.objects.create(
                        cliente=cliente_obj,
                        calle=cleaned_data.get('calle'),
                        numero=cleaned_data.get('numero', ''),
                        
                        ciudad='Santiago',    
                        region='Metropolitana', 
                        codigo_postal=cleaned_data.get('codigo_postal', '')
                     )
                 except Exception as e:
                      print(f"Advertencia: No se pudo guardar la dirección: {e}")
                      

        
        total_pedido = subtotal_calculado + costo_envio_calculado

        
        try:
            nuevo_pedido = Pedido.objects.create(
                cliente=cliente_obj,
                direccion_envio=direccion_obj,
                total=total_pedido,
                estado='pendiente',
                metodo_pago=metodo_pago
                
            )
        except Exception as e:
             return JsonResponse({'success': False, 'message': 'Error interno al crear el pedido. Intenta nuevamente.'})

        
        for item in cart_items_details:
            DetallePedido.objects.create(
                pedido=nuevo_pedido,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'] 
            )
            
            producto = item['producto']
            producto.stock -= item['cantidad']
            producto.save() 

        
        
        
        if metodo_pago == 'transferencia':
             if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

        
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
            
            return JsonResponse({
                'success': True,
                'message': 'Pedido creado correctamente. Redirigiendo para finalizar...', 
                'redirect_url': reverse('subir_comprobante', args=[nuevo_pedido.id])
            })
        else:
            
            return JsonResponse({
                'success': True,
                'message': 'Pedido creado exitosamente.',
                'redirect_url': reverse('generar_recibo_pdf', args=[nuevo_pedido.id])
            })

    else:
        
        first_error = next(iter(form.errors.values()))[0] if form.errors else "Revisa los datos ingresados."
        return JsonResponse({ 'success': False, 'message': f'Error en el formulario: {first_error}' })

def generar_recibo_pdf(request, pedido_id):
    """
    Genera un recibo en PDF para un pedido REAL desde la BD.
    Obtiene datos del cliente SÓLO si hay un Cliente asociado.
    """
    try:
        
        pedido = Pedido.objects.select_related('cliente', 'direccion_envio').get(id=pedido_id)
        detalles = pedido.detalles.select_related('producto').all()
    except Pedido.DoesNotExist:
        raise Http404("Pedido no encontrado")

    
    
    
    cliente_nombre_completo = 'Cliente no registrado'
    cliente_email = 'No disponible'
    cliente_rut = 'No disponible'

    
    if pedido.cliente:
        cliente_nombre_completo = f"{pedido.cliente.nombre} {pedido.cliente.apellidos}"
        cliente_email = pedido.cliente.email
        
        cliente_rut = getattr(pedido.cliente, 'rut', 'No disponible') 


    
    subtotal = sum(d.precio_unitario * d.cantidad for d in detalles)
    total_iva = subtotal * Decimal('0.19') 
    
    costo_envio = Decimal('4500') if pedido.direccion_envio else Decimal('0.00')
    total_pagado = pedido.total 

    logo_path = request.build_absolute_uri(settings.STATIC_URL + 'img/new_black.png')

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
        
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        
        transaccion_existente = TransaccionWebpay.objects.filter(
            pedido=pedido, 
            estado='AUTORIZADO'
        ).first()
        
        if transaccion_existente:
            messages.warning(request, 'Este pedido ya fue pagado.')
            return redirect('generar_recibo_pdf', pedido_id=pedido.id)
        
        _configurar_transbank()
        
        
        buy_order = f"ORD-{pedido.id}-{uuid.uuid4().hex[:8].upper()}"
        
        
        monto = int(pedido.total)

        
        
        return_url = request.build_absolute_uri(reverse('retorno_webpay'))
        
        
        
        tx = Transaction()
        response = tx.create(buy_order, str(request.session.session_key or 'SESSION'), monto, return_url)
        
        
        transaccion = TransaccionWebpay.objects.create(
            pedido=pedido,
            token=response['token'],
            buy_order=buy_order,
            monto=pedido.total,
            estado='PENDIENTE'
        )
        
        
        request.session[f'webpay_token_{pedido.id}'] = response['token']
        
        
        webpay_url = response['url'] + '?token_ws=' + response['token']
        
        
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
        
        _configurar_transbank()
        
        tx = Transaction()
        response = tx.commit(token_ws)
        
        
        transaccion = TransaccionWebpay.objects.filter(token=token_ws).first()
        
        if not transaccion:
            messages.error(request, 'Transacción no encontrada.')
            return redirect('home')
        
        
        transaccion.response_code = str(response.get('response_code', ''))
        transaccion.authorization_code = response.get('authorization_code', '')
        transaccion.payment_type_code = response.get('payment_type_code', '')
        
        
        if 'card_detail' in response and 'card_number' in response['card_detail']:
            transaccion.card_number = response['card_detail']['card_number']
        
        
        if response.get('response_code') == 0 and response.get('status') == 'AUTHORIZED':
            transaccion.estado = 'AUTORIZADO'
            transaccion.save()
            
            
            pedido = transaccion.pedido
            pedido.estado = 'procesando'
            pedido.save()
            
            
            if 'cart' in request.session:
                del request.session['cart']
            
            enviar_recibo_por_email(pedido)
            
            messages.success(request, '¡Pago realizado exitosamente!')
            
            
            context = {
                'pedido': pedido,
                'transaccion': transaccion,
                'exito': True,
                'response': response
            }
            return render(request, 'store/confirmacion_pago.html', context)
        else:
            
            transaccion.estado = 'RECHAZADO'
            transaccion.save()
            
            
            pedido = transaccion.pedido
            pedido.estado = 'cancelado'
            pedido.save()
            
            
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
        
        
        _configurar_transbank()
        
        
        tx = Transaction()
        response = tx.refund(transaccion.token, int(transaccion.monto))
        
        if response.get('type') == 'REVERSED':
            transaccion.estado = 'ANULADO'
            transaccion.save()
            
            
            pedido = transaccion.pedido
            pedido.estado = 'cancelado'
            pedido.save()
            
            
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
        
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        
        transaccion_existente = TransaccionMercadoPago.objects.filter(
            pedido=pedido,
            estado='approved'
        ).first()
        
        if transaccion_existente:
            messages.warning(request, 'Este pedido ya fue pagado.')
            return redirect('generar_recibo_pdf', pedido_id=pedido.id)
        
        sdk = _configurar_mercadopago()
        
        
        items = []
        for detalle in pedido.detalles.all():
            items.append({
                "title": detalle.producto.nombre,
                "quantity": detalle.cantidad,
                "unit_price": float(detalle.precio_unitario),
                "currency_id": "CLP"
            })
        
        
        
        success_url = request.build_absolute_uri(reverse('retorno_mercadopago_success'))
        failure_url = request.build_absolute_uri(reverse('retorno_mercadopago_failure'))
        pending_url = request.build_absolute_uri(reverse('retorno_mercadopago_pending'))
        
        
        
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
        
        
        if preference_response.get('status') != 201:
            error_msg = preference_response.get('response', {}).get('message', 'Error desconocido')
            raise Exception(f"Error de Mercado Pago: {error_msg}")
        
        
        preference = preference_response["response"]
        
        
        
        transaccion = TransaccionMercadoPago.objects.create(
