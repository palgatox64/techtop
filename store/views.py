# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.db.models import Count, Q
from django.db import IntegrityError, transaction
from django.core.validators import validate_email
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
from .forms import ComprobantePagoForm
from .models import PagoTransferencia, ComprobanteTransferencia
from django.db.models import Case, When, Value, IntegerField # Agrega Value e IntegerField por si acaso
from django.db.models import Sum, Count, F, Q, Case, When, Value, IntegerField
# Third-party imports
from decimal import Decimal
from io import BytesIO
from xhtml2pdf import pisa
import re
import csv
import json

# Local imports
from .models import Producto, Marca, Categoria, Cliente, Empleado, Pedido, DetallePedido, Direccion, TransaccionWebpay, TransaccionMercadoPago
from .decorators import admin_required
from .forms import CategoriaForm, MarcaForm, ProductoForm, CheckoutForm
from .validators import validate_chilean_rut

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
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')
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
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')
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
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')
    
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
                total_price += p.precio * qty
                cart_items_data.append({
                    'id': p.id,
                    'name': p.nombre,
                    'quantity': qty,
                    'price': float(p.precio),
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
    
    # Verificar si el producto está activo y tiene stock
    producto_disponible = product.activo and product.stock > 0
    
    context = {
        'product': product,
        'precio_transferencia': precio_transferencia,
        'precio_normal': precio_normal,
        'descuento_porcentaje': descuento_porcentaje,
        'imagenes_adicionales': imagenes_adicionales,
        'producto_disponible': producto_disponible,
    }
    return render(request, 'store/product_detail.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    
    # Validar si el producto está activo y tiene stock
    if not product.activo:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        error_message = 'Este producto no está disponible actualmente.'
        
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': error_message
            })
        else:
            messages.error(request, error_message)
            return redirect('product_detail', product_id=product_id)
    
    if product.stock <= 0:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        error_message = 'Este producto está agotado.'
        
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': error_message
            })
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
            total_price += p.precio * qty
            cart_items_data.append({
                'id': p.id,
                'name': p.nombre,
                'quantity': qty,
                'price': float(p.precio), 
                'image_url': p.imagen.url if p.imagen else '/static/img/placeholder.png' 
            })

        return JsonResponse({
            'success': True,
            'cart_item_count': len(cart),
            'items': cart_items_data,
            'subtotal': float(total_price) 
        })
    else:
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
        precio_transferencia_unitario = product.precio * Decimal('0.97')

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal_transferencia': precio_transferencia_unitario * quantity,
            'subtotal_otros_medios': product.precio * quantity, 
        })
        
        total_transferencia += precio_transferencia_unitario * quantity
        total_otros_medios += product.precio * quantity

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
    """
    Elimina todos los productos del carrito de la sesión.
    Responde a una petición AJAX.
    """
    if request.method == 'POST':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        return JsonResponse({'success': True, 'message': 'El carrito ha sido vaciado.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


def login_view(request):
    """
    Vista de login UNIFICADA que valida tanto empleados como clientes
    """
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        correo = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Validaciones del backend
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
        
        # 🔥 PRIMERO: Intentar buscar en EMPLEADOS
        try:
            empleado = Empleado.objects.get(email=correo)
            
            # Verificar si el empleado está activo
            if not empleado.activo:
                return JsonResponse({
                    'success': False,
                    'message': 'Tu cuenta ha sido desactivada. Contacta al administrador.'
                })
            
            if check_password(password, empleado.pass_hash):
                # Crear sesión de EMPLEADO
                request.session['empleado_id'] = empleado.id_empleado
                request.session['empleado_nombre'] = empleado.nombre
                request.session['empleado_cargo'] = empleado.cargo
                request.session['user_type'] = 'empleado'  # 🔥 Identificador clave
                
                return JsonResponse({
                    'success': True,
                    'message': f'¡Bienvenido, {empleado.nombre}! ({empleado.cargo})',
                    'redirect_url': '/gestion/'  # Redirigir al panel de gestión
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Correo o contraseña incorrectos.'
                })
                
        except Empleado.DoesNotExist:
            # 🔥 SEGUNDO: Si no es empleado, buscar en CLIENTES
            try:
                cliente = Cliente.objects.get(email=correo)
                
                if check_password(password, cliente.pass_hash):
                    # Crear sesión de CLIENTE
                    request.session['cliente_id'] = cliente.id_cliente
                    request.session['cliente_nombre'] = cliente.nombre
                    request.session['user_type'] = 'cliente'  # 🔥 Identificador clave
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'¡Bienvenido de vuelta, {cliente.nombre}!',
                        'redirect_url': '/'  # Redirigir al home
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
            print(f"Error en login_view: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor. Intenta de nuevo.'
            })

def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':
        print(">>> Petición POST recibida en register_view.")

        rut = request.POST.get('rut', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        print(f">>> Datos recibidos: RUT={rut}, Correo={correo}, Nombre={nombre}")

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
            print(">>> Validaciones pasadas. Hasheando contraseña...")
            hashed_password = make_password(password)

            print(">>> Creando el objeto Cliente...")
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
            print(f"Error de integridad en la base de datos: {e}")
            if 'rut' in str(e).lower():
                messages.error(request, 'El RUT ya está en uso.')
            elif 'UNIQUE constraint' in str(e) or 'unique' in str(e).lower():
                messages.error(request, 'El correo electrónico ya está en uso.')
            else:
                messages.error(request, 'Error al crear la cuenta. Por favor, intenta de nuevo.')
            return redirect('register')
        
        except Exception as e:
            print(f"Error inesperado al guardar en la base de datos: {e}")
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
    return render(request, 'gestion/panel.html')

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
            form.save()
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

    # Calcular precio de transferencia
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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

    # Calcular precio de transferencia
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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

    # Calcular precio de transferencia
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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

    # Calcular precio de transferencia
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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

    # Calcular precio de transferencia
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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

    # Calcular precio de transferencia
    for product in products:
        product.precio_transferencia = product.precio * Decimal('0.97')

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
        if products:
            for product in products:
                product.precio_transferencia = product.precio * Decimal('0.97')
    context = {
        'products': products,
        'search_query': query,
    }
    return render(request, 'store/search_results.html', context)

# store/views.py

def checkout_view(request):
    """
    Muestra la página de checkout, rellenando los datos si el usuario está logueado.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Tu carro está vacío.')
        return redirect('view_cart')

    # (Lógica para calcular items y totales - sin cambios)
    product_ids = cart.keys()
    products_in_cart = Producto.objects.filter(id__in=product_ids)
    cart_items = []
    total_transferencia = Decimal('0.00')
    total_otros_medios = Decimal('0.00')
    for product in products_in_cart:
        product_id_str = str(product.id)
        quantity = cart[product_id_str]['quantity']
        precio_transferencia_unitario = product.precio * Decimal('0.97')
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal_transferencia': precio_transferencia_unitario * quantity,
            'subtotal_otros_medios': product.precio * quantity,
        })
        total_transferencia += precio_transferencia_unitario * quantity
        total_otros_medios += product.precio * quantity

    # --- LÓGICA MEJORADA PARA RELLENAR EL FORMULARIO ---
    initial_data = {}
    user_type = request.session.get('user_type')
    user = None # Variable para guardar el objeto Cliente o Empleado

    print(f"DEBUG: User type in session: {user_type}") # Para depurar

    if user_type == 'cliente':
        cliente_id = request.session.get('cliente_id')
        if cliente_id:
            try:
                user = get_object_or_404(Cliente, id_cliente=cliente_id)
                print(f"DEBUG: Cliente encontrado: {user}") # Para depurar
            except Exception as e:
                print(f"Error buscando Cliente ID {cliente_id}: {e}")
                request.session.flush() # Limpiar sesión si el ID es inválido

    elif user_type == 'empleado':
        empleado_id = request.session.get('empleado_id')
        if empleado_id:
            try:
                user = get_object_or_404(Empleado, id_empleado=empleado_id)
                print(f"DEBUG: Empleado encontrado: {user}") # Para depurar
            except Exception as e:
                print(f"Error buscando Empleado ID {empleado_id}: {e}")
                request.session.flush() # Limpiar sesión si el ID es inválido

    # Si encontramos un usuario (Cliente o Empleado), llenamos initial_data
    if user:
        initial_data = {
            'nombre': user.nombre,
            'apellidos': user.apellidos,
            'rut': getattr(user, 'rut', ''), # Usamos getattr por si algún modelo no tuviera rut (aunque ambos lo tienen)
            'email': user.email,
            'telefono': user.telefono,
        }
        print(f"DEBUG: Initial data set: {initial_data}") # Para depurar
    else:
         print("DEBUG: No user found in session or DB, form will be empty.") # Para depurar


    # Pasamos los datos iniciales al formulario
    # Si initial_data está vacío, el formulario aparecerá en blanco
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
    Recibe el POST del checkout, valida, crea Pedido/Detalles/Direccion (SOLO con campos existentes),
    descuenta stock y redirige al PDF.
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

        # --- OBTENER DATOS DEL CARRITO Y VALIDAR STOCK (Sin cambios) ---
        product_ids = cart.keys()
        products_in_cart = Producto.objects.select_for_update().filter(id__in=product_ids)
        cart_items_details = []
        subtotal_calculado = Decimal('0.00')
        product_map = {str(p.id): p for p in products_in_cart}
        for product_id_str, item_data in cart.items():
            product = product_map.get(product_id_str)
            if not product: return JsonResponse({'success': False, 'message': f'Producto ID {product_id_str} no disponible.'})
            quantity = item_data['quantity']
            if product.stock < quantity: return JsonResponse({'success': False, 'message': f'Stock insuficiente para "{product.nombre}".'})
            precio_unitario_a_guardar = product.precio * Decimal('0.97') if metodo_pago == 'transferencia' else product.precio
            cart_items_details.append({'producto': product, 'cantidad': quantity, 'precio_unitario': precio_unitario_a_guardar})
            subtotal_calculado += precio_unitario_a_guardar * quantity

        # --- BUSCAR CLIENTE LOGUEADO (Sin cambios) ---
        cliente_obj = None
        if request.session.get('user_type') == 'cliente':
            try:
                cliente_obj = Cliente.objects.get(id_cliente=request.session.get('cliente_id'))
            except Cliente.DoesNotExist:
                request.session.flush()

        # --- MANEJAR DIRECCIÓN Y COSTO DE ENVÍO (Sin cambios) ---
        direccion_obj = None
        costo_envio_calculado = Decimal('0.00')
        if tipo_entrega == 'delivery':
            costo_envio_calculado = Decimal('4500')
            if cliente_obj:
                 try:
                     direccion_obj = Direccion.objects.create(
                        cliente=cliente_obj,
                        calle=cleaned_data.get('calle'),
                        numero=cleaned_data.get('numero', ''),
                        ciudad='Santiago', # Temporal
                        region='Metropolitana', # Temporal
                        codigo_postal=cleaned_data.get('codigo_postal', '')
                     )
                 except Exception as e:
                      print(f"Error al crear dirección: {e}")
                      direccion_obj = None

        # --- CALCULAR TOTAL FINAL (Sin cambios) ---
        total_final = subtotal_calculado + costo_envio_calculado

        # --- CREAR EL OBJETO Pedido (CORREGIDO: SIN CAMPOS EXTRA) ---
        try:
            # Quitamos los campos nombre_cliente, apellidos_cliente, rut_cliente,
            # email_cliente, telefono_cliente, metodo_pago, tipo_entrega, costo_envio
            # porque NO existen en el modelo Pedido actual.
            pedido_data = {
                'cliente': cliente_obj,        # Clave foránea a Cliente (puede ser None)
                'direccion_envio': direccion_obj, # Clave foránea a Direccion (puede ser None)
                'total': total_final,          # DecimalField
                'estado': 'procesando',        # CharField
                # 'fecha_pedido' se añade automáticamente (auto_now_add=True)
            }
            nuevo_pedido = Pedido.objects.create(**pedido_data)
            # El ID se genera automáticamente

        except Exception as e:
             # Si aún da error aquí, será por otra razón (ej: tipo de dato incorrecto)
             print(f"ERROR AL CREAR PEDIDO: {e}")
             # Mensaje de error genérico para el usuario
             return JsonResponse({'success': False, 'message': 'Hubo un error al registrar tu pedido. Intenta de nuevo más tarde.'})


        # --- CREAR LOS OBJETOS DetallePedido Y DESCONTAR STOCK (Sin cambios) ---
        for item in cart_items_details:
            try:
                DetallePedido.objects.create(
                    pedido=nuevo_pedido,
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario']
                )
                producto_a_actualizar = item['producto']
                producto_a_actualizar.stock -= item['cantidad']
                producto_a_actualizar.save(update_fields=['stock', 'activo'])
            except Exception as e:
                print(f"Error al crear DetallePedido o actualizar stock para {item['producto'].nombre}: {e}")
                raise e # Re-lanzar para rollback

        # --- LIMPIAR CARRITO ---
        # IMPORTANTE: Solo limpiar el carrito si NO es pago con Webpay o Mercado Pago
        # Para estos métodos, se limpiará después de confirmar el pago
        if metodo_pago not in ['webpay', 'mercadopago']:
            request.session['cart'] = {}
            request.session.modified = True

        # --- REDIRIGIR SEGÚN EL MÉTODO DE PAGO ---
        if metodo_pago == 'webpay':
            # Redirigir a la vista de inicio de pago de Webpay
            redirect_url = reverse('iniciar_pago_webpay', args=[nuevo_pedido.id])
            return JsonResponse({
                'success': True,
                'message': 'Redirigiendo a Webpay para completar el pago...',
                'redirect_url': redirect_url
            })
        elif metodo_pago == 'mercadopago':
            # Redirigir a la vista de inicio de pago de Mercado Pago
            redirect_url = reverse('iniciar_pago_mercadopago', args=[nuevo_pedido.id])
            return JsonResponse({
                'success': True,
                'message': 'Redirigiendo a Mercado Pago para completar el pago...',
                'redirect_url': redirect_url
            })
        elif metodo_pago == 'transferencia':
            # --- CAMBIO AQUÍ ---
            # Redirigir a la nueva vista de subida de comprobantes
            redirect_url = reverse('subir_comprobante', args=[nuevo_pedido.id])
            return JsonResponse({
                'success': True,
                'message': 'Pedido creado. Redirigiendo para subir comprobante...',
                'redirect_url': redirect_url
            })
        else:
            # Para otros métodos de pago, ir directo al PDF
            redirect_url = reverse('generar_recibo_pdf', args=[nuevo_pedido.id])
            return JsonResponse({
                'success': True,
                'message': '¡Pedido recibido con éxito! Generando recibo...',
                'redirect_url': redirect_url
            })

    else:
        # El formulario NO es válido (Sin cambios)
        error_message = "Error en el formulario. Por favor, revisa tus datos."
        if form.errors:
            first_error_field = next(iter(form.errors))
            first_error_msg = form.errors[first_error_field][0]
            error_message = f"Error en '{first_error_field.replace('_',' ').title()}': {first_error_msg}"
        return JsonResponse({ 'success': False, 'message': error_message })

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
        print(f"xhtml2pdf error: {pdf.err}")
        return HttpResponse(f"Error al generar el PDF: {pdf.err}. Revisa los logs.", status=500)


# ==================== CHATBOT INTELIGENTE ====================

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_view(request):
    """
    Vista para procesar las consultas del chatbot y generar respuestas inteligentes.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').lower().strip()
        
        # Generar respuesta basada en el mensaje del usuario
        response = generate_chatbot_response(user_message)
        
        return JsonResponse(response)
    
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return JsonResponse({
            'message': 'Error al procesar el mensaje. Por favor, intenta de nuevo.',
            'data': None
        }, status=400)
    except Exception as e:
        print(f"Error en chatbot_view: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'message': f'Lo siento, ocurrió un error: {str(e)}',
            'data': None
        }, status=500)


def generate_chatbot_response(message):
    """
    Genera una respuesta inteligente basada en el mensaje del usuario.
    Utiliza procesamiento de lenguaje natural mejorado.
    """
    original_message = message
    message = message.lower().strip()
    
    # Palabras irrelevantes para filtrar
    stop_words = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al', 'por', 'para', 'en', 'y', 'o']
    
    # Extraer palabras clave (sin palabras irrelevantes)
    words = [w for w in message.split() if w not in stop_words and len(w) > 1]
    
    # ========== RESPUESTAS PRIORITARIAS (NO BÚSQUEDA) ==========
    
    # 1. SALUDOS (PRIMERO - Alta prioridad)
    if any(word in message for word in ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'hey', 'hi', 'saludos']) and len(words) <= 3:
        return {
            'message': '👋 <strong>¡Hola! Bienvenido a TechTop</strong><br><br>Soy tu asistente virtual inteligente. Puedo ayudarte con:<br><br>🔍 <strong>Búsqueda rápida de productos:</strong><br>• "Quiero un parlante Bluetooth"<br>• "Muéstrame medidores láser"<br>• "Cargadores de batería"<br><br>💡 <strong>Recomendaciones personalizadas:</strong><br>• "¿Qué me recomiendas para mi auto?"<br>• "Productos más vendidos"<br>• "Lo más económico"<br><br>📋 <strong>Información útil:</strong><br>• Ver categorías y marcas<br>• Seguimiento de pedidos<br>• Métodos de pago y garantías<br><br><em>¿En qué puedo ayudarte hoy?</em>',
            'data': {'type': 'welcome'}
        }
    
    # 2. AGRADECIMIENTOS
    if any(word in message for word in ['gracias', 'gracias!', 'thank', 'excelente', 'perfecto', 'genial']) and len(words) <= 3:
        return {
            'message': '😊 ¡De nada! Es un placer ayudarte.<br><br>¿Necesitas algo más? Puedo ayudarte a encontrar productos específicos o resolver cualquier duda.',
            'data': None
        }
    
    # 3. AYUDA
    if any(word in message for word in ['ayuda', 'help', 'que puedes hacer', 'qué puedes hacer', 'como funciona', 'cómo funciona']):
        return {
            'message': '💡 <strong>Soy tu asistente de compras inteligente</strong><br><br><strong>🎯 Puedo ayudarte a:</strong><br><br>1️⃣ <strong>Encontrar productos exactos:</strong><br>• "Parlante Bluetooth para exteriores"<br>• "Medidor láser de distancia"<br>• "Radio Android para Nissan"<br><br>2️⃣ <strong>Darte recomendaciones:</strong><br>• "¿Qué productos recomiendas?"<br>• "Lo más vendido"<br>• "Productos económicos"<br><br>3️⃣ <strong>Comparar y filtrar:</strong><br>• "Diferencia entre medidores"<br>• "Compresores más baratos"<br>• "Productos de marca Xiaomi"<br><br>4️⃣ <strong>Resolver dudas:</strong><br>• Métodos de pago<br>• Seguimiento de pedidos<br>• Garantías y devoluciones<br><br><em>¡Escribe cualquier consulta y te ayudaré!</em>',
            'data': {'type': 'help'}
        }
    
    # 4. SEGUIMIENTO DE PEDIDOS
    if any(word in message for word in ['pedido', 'orden', 'compra', 'rastrear', 'seguimiento', 'envío', 'envio', 'tracking', 'donde esta', 'dónde está']):
        return {
            'message': '📦 <strong>Seguimiento de Pedidos</strong><br><br>Para rastrear tu pedido en tiempo real:<br><br>1️⃣ Visita: <a href="/seguimiento-compra/" style="color: #667eea; font-weight: bold;">Seguimiento de Compra</a><br>2️⃣ Ingresa tu número de orden<br>3️⃣ Confirma con tu correo electrónico<br><br>ℹ️ <strong>Recibirás información sobre:</strong><br>• Estado actual del pedido<br>• Fecha estimada de entrega<br>• Número de guía de envío<br><br>¿Necesitas ayuda con algo más?',
            'data': {'type': 'link', 'url': '/seguimiento-compra/'}
        }
    
    # 5. MÉTODOS DE PAGO
    if any(word in message for word in ['pago', 'pagar', 'tarjeta', 'transferencia', 'efectivo', 'método', 'forma', 'como pago', 'cómo pago']):
        return {
            'message': '💳 <strong>Métodos de Pago Disponibles</strong><br><br>✅ <strong>Tarjeta de crédito/débito</strong><br>   • Visa, Mastercard, American Express<br>   • Pago seguro y encriptado<br><br>💸 <strong>Transferencia bancaria</strong><br>   • <span style="color: #48bb78; font-weight: bold;">¡3% de descuento!</span><br>   • Procesamiento en 24-48 hrs<br><br>💵 <strong>Efectivo en tienda</strong><br>   • Paga al retirar tu producto<br>   • Sin cargos adicionales<br><br>🔒 <strong>Todos los pagos son 100% seguros</strong><br><br>¿Tienes alguna pregunta sobre un método específico?',
            'data': {'type': 'payment_methods'}
        }
    
    # 6. GARANTÍAS
    if any(word in message for word in ['garantia', 'garantía', 'devolución', 'devolucion', 'cambio', 'retorno', 'defectuoso']):
        return {
            'message': '🛡️ <strong>Garantías y Devoluciones</strong><br><br>✅ <strong>Todos nuestros productos incluyen:</strong><br>• Garantía del fabricante<br>• Certificado de autenticidad<br>• Soporte técnico<br><br>🔄 <strong>Política de devolución:</strong><br>• 30 días para cambios y devoluciones<br>• Producto en perfecto estado<br>• Con embalaje original<br><br>📞 <strong>Para más detalles:</strong><br>• <a href="/garantias/" style="color: #667eea; font-weight: bold;">Ver Política Completa</a><br>• <a href="/contacto/" style="color: #667eea; font-weight: bold;">Contactar Soporte</a><br><br>¿Tienes un caso específico?',
            'data': {'type': 'link', 'url': '/garantias/'}
        }
    
    # 7. CONTACTO
    if any(word in message for word in ['contacto', 'teléfono', 'telefono', 'dirección', 'direccion', 'ubicación', 'ubicacion', 'horario', 'llamar', 'visitar']):
        return {
            'message': '📞 <strong>¿Cómo contactarnos?</strong><br><br>• <a href="/contacto/" style="color: #667eea; font-weight: bold;">Formulario de Contacto</a><br>• <a href="/centro-ayuda/" style="color: #667eea; font-weight: bold;">Centro de Ayuda</a><br><br>⏰ <strong>Horario de atención:</strong><br>Lunes a Viernes: 9:00 - 18:00<br>Sábados: 10:00 - 14:00<br><br>¿Necesitas ayuda con algo específico?',
            'data': {'type': 'contact'}
        }
    
    # ========== BÚSQUEDA DE PRODUCTOS ==========
    
    # 8. PALABRAS CLAVE DE BÚSQUEDA EXPLÍCITA
    search_keywords = ['quiero', 'busco', 'necesito', 'muestra', 'muestrame', 'mostrame', 'ver', 'buscar', 
                      'encontrar', 'tienes', 'tienen', 'vende', 'venden', 'precio', 'cuanto', 'cuesta',
                      'recomienda', 'recomendación', 'sugerir', 'dame']
    
    is_explicit_search = any(word in message for word in search_keywords)
    
    # 9. SOLICITUD DE VER PRODUCTOS GENERALES
    if any(word in message for word in ['productos', 'catalogo', 'catálogo', 'tienda', 'mostrar todo', 'todo']):
        if any(word in message for word in ['todos', 'ver', 'mostrar', 'cuales', 'qué', 'que']):
            productos = Producto.objects.all().order_by('-fecha_pub')[:6]
            if productos:
                return crear_respuesta_productos(productos, "productos destacados")
    
    # 10. RECOMENDACIONES Y PRODUCTOS DESTACADOS
    if any(word in message for word in ['recomien', 'sugerir', 'mejor', 'mejores', 'destacado', 'popular', 'vendido']):
        productos = Producto.objects.filter(stock__gt=0).order_by('-fecha_pub')[:6]
        return crear_respuesta_productos(productos, "productos recomendados")
    
    # 11. CONSULTAS SOBRE PRECIOS
    if any(word in message for word in ['barato', 'económico', 'oferta', 'descuento', 'rebaja']):
        productos = Producto.objects.filter(stock__gt=0).order_by('precio')[:6]
        return crear_respuesta_productos(productos, "productos más económicos")
    elif any(word in message for word in ['caro', 'premium', 'mejor calidad', 'alta gama']):
        productos = Producto.objects.filter(stock__gt=0).order_by('-precio')[:6]
        return crear_respuesta_productos(productos, "productos premium")
    
    # 12. BÚSQUEDA POR CATEGORÍA O MARCA
    categorias = Categoria.objects.all()
    for categoria in categorias:
        cat_lower = categoria.nombre.lower()
        cat_normalized = cat_lower.replace('-', ' ').replace('_', ' ')
        message_normalized = message.replace('-', ' ').replace('_', ' ')
        
        if cat_lower in message or cat_normalized in message_normalized:
            productos = Producto.objects.filter(categoria=categoria, stock__gt=0)[:6]
            if productos:
                return crear_respuesta_productos(productos, f"productos de {categoria.nombre}")
    
    # 13. BÚSQUEDA POR MARCA
    marcas = Marca.objects.all()
    for marca in marcas:
        marca_lower = marca.nombre.lower()
        if marca_lower in message:
            productos = Producto.objects.filter(marca=marca, stock__gt=0)[:6]
            if productos:
                return crear_respuesta_productos(productos, f"productos de {marca.nombre}")
    
    # 14. LISTAR CATEGORÍAS
    if any(word in message for word in ['categoria', 'categoría', 'categorias', 'categorías', 'tipo', 'tipos', 'secciones']):
        categorias = Categoria.objects.all()
        if categorias:
            response_text = "📁 <strong>Nuestras Categorías de Productos:</strong><br><br>"
            for cat in categorias:
                count = Producto.objects.filter(categoria=cat, stock__gt=0).count()
                if count > 0:
                    response_text += f"• <strong>{cat.nombre}</strong> - {count} productos disponibles<br>"
            response_text += "<br><em>Escribe el nombre de una categoría para ver sus productos</em>"
            
            return {
                'message': response_text,
                'data': {'type': 'categorias', 'categorias': [c.nombre for c in categorias]}
            }
    
    # 15. LISTAR MARCAS
    if any(word in message for word in ['marca', 'marcas', 'fabricante', 'fabricantes']):
        marcas = Marca.objects.all()
        if marcas:
            response_text = "🏷️ <strong>Marcas Disponibles:</strong><br><br>"
            for marca in marcas:
                count = Producto.objects.filter(marca=marca, stock__gt=0).count()
                if count > 0:
                    response_text += f"• <strong>{marca.nombre}</strong> - {count} productos<br>"
            response_text += "<br><em>Escribe el nombre de una marca para ver sus productos</em>"
            
            return {
                'message': response_text,
                'data': {'type': 'marcas', 'marcas': [m.nombre for m in marcas]}
            }
    
    # 16. BÚSQUEDA INTELIGENTE DE PRODUCTOS
    if is_explicit_search and len(words) >= 1:
        productos_encontrados = buscar_productos_inteligente(original_message, words)
        if productos_encontrados and len(productos_encontrados) > 0:
            return crear_respuesta_productos(productos_encontrados, "productos encontrados")
    
    # ========== RESPUESTA POR DEFECTO ==========
    return {
        'message': '🤔 <strong>No estoy seguro de cómo ayudarte con eso</strong><br><br>Pero puedo ayudarte con:<br><br>💬 <strong>Búsqueda de productos:</strong><br>• "Quiero ver parlantes Bluetooth"<br>• "Necesito un medidor láser"<br>• "Mostrar radios Android"<br><br>🔍 <strong>Explorar catálogo:</strong><br>• "Ver todas las categorías"<br>• "Productos más baratos"<br>• "¿Qué me recomiendas?"<br><br>ℹ️ <strong>Información:</strong><br>• "Métodos de pago"<br>• "Seguimiento de pedido"<br>• "Garantías"<br><br><em>Escribe "ayuda" para ver más opciones</em>',
        'data': None
    }


def buscar_productos_inteligente(mensaje_original, palabras_clave):
    """
    Búsqueda inteligente de productos usando múltiples criterios.
    Prioriza coincidencias exactas en categorías y marcas.
    """
    mensaje_limpio = mensaje_original.lower().strip()
    
    # Diccionario de sinónimos para búsqueda más inteligente
    sinonimos = {
        'parlante': ['parlante', 'parlantes', 'bocina', 'bocinas', 'altavoz', 'speaker', 'bluetooth'],
        'medidor': ['medidor', 'medidores', 'nivel', 'laser', 'distancia', 'angulo'],
        'cargador': ['cargador', 'cargadores', 'bateria', 'batería', 'fosfor'],
        'compresor': ['compresor', 'compresores', 'aire', 'inflador'],
        'radio': ['radio', 'radios', 'android', 'pantalla', 'multimedia', 'carplay'],
        'scanner': ['scanner', 'escaner', 'diagnostico', 'obdii', 'obd2', 'automotriz'],
    }
    
    # Expandir palabras clave con sinónimos
    palabras_expandidas = list(palabras_clave)
    for palabra in palabras_clave:
        for key, values in sinonimos.items():
            if palabra.lower() in values:
                palabras_expandidas.extend(values)
                break
    
    # PASO 1: Buscar primero en categorías (más específico)
    categorias = Categoria.objects.all()
    for categoria in categorias:
        cat_nombre_lower = categoria.nombre.lower()
        cat_words = cat_nombre_lower.split()
        
        if cat_nombre_lower in mensaje_limpio:
            productos = Producto.objects.filter(categoria=categoria)[:6]
            if productos:
                return productos
        
        for cat_word in cat_words:
            if len(cat_word) > 3 and cat_word in mensaje_limpio:
                productos = Producto.objects.filter(categoria=categoria)[:6]
                if productos:
                    return productos
        
        for palabra in palabras_expandidas:
            if palabra.lower() in cat_nombre_lower or cat_nombre_lower in palabra.lower():
                productos = Producto.objects.filter(categoria=categoria)[:6]
                if productos:
                    return productos
    
    # PASO 2: Buscar en marcas
    marcas = Marca.objects.all()
    for marca in marcas:
        marca_nombre_lower = marca.nombre.lower()
        if marca_nombre_lower in mensaje_limpio or any(marca_nombre_lower in palabra for palabra in palabras_expandidas):
            productos = Producto.objects.filter(marca=marca)[:6]
            if productos:
                return productos
    
    # PASO 3: Búsqueda general por palabras clave
    query = Q()
    for palabra in palabras_expandidas:
        if len(palabra) > 1:
            query |= Q(nombre__icontains=palabra)
            query |= Q(descripcion__icontains=palabra)
    
    if mensaje_limpio:
        query |= Q(nombre__icontains=mensaje_limpio)
        query |= Q(descripcion__icontains=mensaje_limpio)
    
    if query:
        productos = Producto.objects.filter(query).distinct()[:6]
        if productos:
            return productos
    
    # PASO 4: Búsqueda flexible
    if palabras_clave:
        query_flexible = Q()
        for palabra in palabras_clave:
            if len(palabra) > 2:
                query_flexible |= Q(nombre__icontains=palabra)
        
        if query_flexible:
            productos = Producto.objects.filter(query_flexible).distinct()[:6]
            if productos:
                return productos
    
    return Producto.objects.all()[:6]


def crear_respuesta_productos(productos, contexto="productos"):
    """
    Crea una respuesta formateada con los productos encontrados.
    """
    if not productos:
        return {
            'message': 'No encontré productos que coincidan con tu búsqueda. 🤔<br><br>Intenta:<br>• Usar otras palabras clave<br>• Ver todas las categorías<br>• Escribir "ver productos" para ver el catálogo',
            'data': None
        }
    
    productos_data = []
    for p in productos:
        precio_transferencia = float(p.precio * Decimal('0.97'))
        imagen_url = p.imagen.url if p.imagen else '/static/img/no-image.png'
        
        productos_data.append({
            'id': p.id,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'precio_transferencia': precio_transferencia,
            'imagen': imagen_url,
            'marca': p.marca.nombre,
            'categoria': p.categoria.nombre,
            'stock': p.stock
        })
    
    count = len(productos)
    header = f'🎯 <strong>Encontré {count} producto{"s" if count > 1 else ""}:</strong><br><br>'
    
    response_text = header
    response_text += '<div class="chatbot-products-grid">'
    
    for p in productos_data:
        disponible = "✅ Disponible" if p['stock'] > 0 else "❌ Sin stock"
        response_text += f'''
        <div class="chatbot-product-card" onclick="window.location.href='/producto/{p['id']}/'">
            <img src="{p['imagen']}" alt="{p['nombre']}" onerror="this.src='/static/img/no-image.png'">
            <div class="chatbot-product-info">
                <h4>{p['nombre']}</h4>
                <p class="brand">{p['marca']} • {p['categoria']}</p>
                <p class="price">💳 ${p['precio']:,.0f}</p>
                <p class="price-transfer">💸 ${p['precio_transferencia']:,.0f} (Transferencia)</p>
                <p class="stock">{disponible}</p>
            </div>
        </div>
        '''
    
    response_text += '</div><br><em>Haz clic en cualquier producto para ver más detalles</em>'
    
    return {
        'message': response_text,
        'data': {
            'type': 'productos',
            'productos': productos_data
        }
    }


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
    print(f"=== INICIANDO PAGO WEBPAY PARA PEDIDO {pedido_id} ===")
    try:
        # Obtener el pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)
        print(f"Pedido encontrado: ID={pedido.id}, Total={pedido.total}")
        
        # Verificar que no exista ya una transacción autorizada para este pedido
        transaccion_existente = TransaccionWebpay.objects.filter(
            pedido=pedido, 
            estado='AUTORIZADO'
        ).first()
        
        if transaccion_existente:
            print(f"Transacción ya existe y está autorizada")
            messages.warning(request, 'Este pedido ya fue pagado.')
            return redirect('generar_recibo_pdf', pedido_id=pedido.id)
        
        # Configurar Transbank
        print("Configurando Transbank...")
        _configurar_transbank()
        
        # Generar un buy_order único
        buy_order = f"ORD-{pedido.id}-{uuid.uuid4().hex[:8].upper()}"
        print(f"Buy Order generado: {buy_order}")
        
        # Obtener el monto (convertir a entero, Transbank no acepta decimales)
        monto = int(pedido.total)
        print(f"Monto a cobrar: {monto}")
        
        # URLs de retorno
        return_url = request.build_absolute_uri(reverse('retorno_webpay'))
        print(f"URL de retorno: {return_url}")
        
        # Crear la transacción en Webpay
        print("Creando transacción en Transbank...")
        # El SDK v4.0.0 usa esta firma: create(buy_order, session_id, amount, return_url)
        tx = Transaction()
        response = tx.create(buy_order, str(request.session.session_key or 'SESSION'), monto, return_url)
        print(f"Respuesta de Transbank: {response}")
        
        # Guardar la transacción en la base de datos
        transaccion = TransaccionWebpay.objects.create(
            pedido=pedido,
            token=response['token'],
            buy_order=buy_order,
            monto=pedido.total,
            estado='PENDIENTE'
        )
        print(f"Transacción guardada en BD: ID={transaccion.id}")
        
        # Guardar el token en la sesión para validar posteriormente
        request.session[f'webpay_token_{pedido.id}'] = response['token']
        
        # Construir la URL de Webpay
        webpay_url = response['url'] + '?token_ws=' + response['token']
        print(f"Redirigiendo a: {webpay_url}")
        
        # Redirigir al usuario a Webpay
        return redirect(webpay_url)
        
    except Exception as e:
        print(f"Error al iniciar pago Webpay: {e}")
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('checkout')


@transaction.atomic
def retorno_webpay(request):
    """
    Vista que recibe el retorno desde Webpay después del pago.
    Confirma la transacción y actualiza el estado del pedido.
    """
    token_ws = request.GET.get('token_ws') or request.POST.get('token_ws')
    
    print(f"=== RETORNO DE WEBPAY ===")
    print(f"Token recibido: {token_ws}")
    
    if not token_ws:
        messages.error(request, 'Token de transacción no válido.')
        return redirect('home')
    
    try:
        # Configurar Transbank
        _configurar_transbank()
        
        # Confirmar la transacción con Transbank
        print("Confirmando transacción con Transbank...")
        tx = Transaction()
        response = tx.commit(token_ws)
        print(f"Respuesta de confirmación: {response}")
        
        # Buscar la transacción en la base de datos
        transaccion = TransaccionWebpay.objects.filter(token=token_ws).first()
        
        if not transaccion:
            print("ERROR: Transacción no encontrada en BD")
            messages.error(request, 'Transacción no encontrada.')
            return redirect('home')
        
        print(f"Transacción encontrada: ID={transaccion.id}, Pedido={transaccion.pedido.id}")
        
        # Actualizar la transacción con los datos de respuesta
        transaccion.response_code = str(response.get('response_code', ''))
        transaccion.authorization_code = response.get('authorization_code', '')
        transaccion.payment_type_code = response.get('payment_type_code', '')
        
        # Obtener últimos 4 dígitos de la tarjeta si están disponibles
        if 'card_detail' in response and 'card_number' in response['card_detail']:
            transaccion.card_number = response['card_detail']['card_number']
        
        # Verificar si el pago fue aprobado
        print(f"Estado de respuesta: response_code={response.get('response_code')}, status={response.get('status')}")
        if response.get('response_code') == 0 and response.get('status') == 'AUTHORIZED':
            print("¡PAGO APROBADO!")
            transaccion.estado = 'AUTORIZADO'
            transaccion.save()
            
            # Actualizar el estado del pedido
            pedido = transaccion.pedido
            pedido.estado = 'procesando'
            pedido.save()
            
            # Limpiar el carrito
            if 'cart' in request.session:
                del request.session['cart']
            
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
        print(f"Error en retorno Webpay: {e}")
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
        print(f"Error al anular transacción: {e}")
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
    print(f"=== INICIANDO PAGO MERCADO PAGO PARA PEDIDO {pedido_id} ===")
    try:
        # Obtener el pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)
        print(f"Pedido encontrado: ID={pedido.id}, Total={pedido.total}")
        
        # Verificar que no exista ya una transacción aprobada
        transaccion_existente = TransaccionMercadoPago.objects.filter(
            pedido=pedido,
            estado='approved'
        ).first()
        
        if transaccion_existente:
            print(f"Transacción ya existe y está aprobada")
            messages.warning(request, 'Este pedido ya fue pagado.')
            return redirect('generar_recibo_pdf', pedido_id=pedido.id)
        
        # Configurar Mercado Pago
        print("Configurando Mercado Pago...")
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
        
        print(f"Items preparados: {len(items)} productos")
        
        # URLs de retorno
        success_url = request.build_absolute_uri(reverse('retorno_mercadopago_success'))
        failure_url = request.build_absolute_uri(reverse('retorno_mercadopago_failure'))
        pending_url = request.build_absolute_uri(reverse('retorno_mercadopago_pending'))
        
        print(f"URLs configuradas:")
        print(f"  - Success: {success_url}")
        print(f"  - Failure: {failure_url}")
        print(f"  - Pending: {pending_url}")
        
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
        
        print("Creando preferencia en Mercado Pago...")
        preference_response = sdk.preference().create(preference_data)
        print(f"Respuesta completa: {preference_response}")
        
        # Verificar si hay error en la respuesta
        if preference_response.get('status') != 201:
            error_msg = preference_response.get('response', {}).get('message', 'Error desconocido')
            print(f"ERROR en API de Mercado Pago: {error_msg}")
            raise Exception(f"Error de Mercado Pago: {error_msg}")
        
        # La respuesta exitosa viene en preference_response["response"]
        preference = preference_response["response"]
        
        print(f"Preferencia creada exitosamente: {preference['id']}")
        
        # Guardar la transacción en la base de datos
        transaccion = TransaccionMercadoPago.objects.create(
            pedido=pedido,
            preference_id=preference['id'],
            monto=pedido.total,
            estado='pending'
        )
        print(f"Transacción guardada en BD: ID={transaccion.id}")
        
        # Obtener la URL de inicio de pago (usar sandbox para ambiente de pruebas)
        init_point = preference.get('sandbox_init_point') or preference.get('init_point')
        print(f"Redirigiendo a: {init_point}")
        print(f"NOTA: Las back_urls pueden no funcionar con localhost. Considera usar ngrok para pruebas.")
        
        # Redirigir al usuario a Mercado Pago
        return redirect(init_point)
        
    except Exception as e:
        print(f"Error al iniciar pago Mercado Pago: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('checkout')


@transaction.atomic
def retorno_mercadopago_success(request):
    """Maneja el retorno exitoso desde Mercado Pago"""
    print(f"=== RETORNO EXITOSO DE MERCADO PAGO ===")
    return _procesar_retorno_mercadopago(request, 'approved')


@transaction.atomic
def retorno_mercadopago_failure(request):
    """Maneja el retorno fallido desde Mercado Pago"""
    print(f"=== RETORNO FALLIDO DE MERCADO PAGO ===")
    return _procesar_retorno_mercadopago(request, 'rejected')


@transaction.atomic
def retorno_mercadopago_pending(request):
    """Maneja el retorno pendiente desde Mercado Pago"""
    print(f"=== RETORNO PENDIENTE DE MERCADO PAGO ===")
    return _procesar_retorno_mercadopago(request, 'pending')


def _procesar_retorno_mercadopago(request, estado_esperado):
    """
    Procesa el retorno desde Mercado Pago.
    """
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    external_reference = request.GET.get('external_reference')
    preference_id = request.GET.get('preference_id')
    
    print(f"Parámetros recibidos: payment_id={payment_id}, status={status}, external_reference={external_reference}")
    
    try:
        # Buscar la transacción por preference_id o external_reference
        if preference_id:
            transaccion = TransaccionMercadoPago.objects.filter(preference_id=preference_id).first()
        elif external_reference:
            pedido = Pedido.objects.get(id=external_reference)
            transaccion = TransaccionMercadoPago.objects.filter(pedido=pedido).first()
        else:
            messages.error(request, 'No se pudo identificar la transacción.')
            return redirect('home')
        
        if not transaccion:
            print("ERROR: Transacción no encontrada en BD")
            messages.error(request, 'Transacción no encontrada.')
            return redirect('home')
        
        print(f"Transacción encontrada: ID={transaccion.id}, Pedido={transaccion.pedido.id}")
        
        # Si hay payment_id, consultar detalles del pago
        if payment_id:
            sdk = _configurar_mercadopago()
            payment_info = sdk.payment().get(payment_id)
            
            if payment_info["status"] == 200:
                payment_data = payment_info["response"]
                
                # Actualizar transacción con datos del pago
                transaccion.payment_id = str(payment_id)
                transaccion.estado = payment_data.get('status', status)
                transaccion.status_detail = payment_data.get('status_detail', '')
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
                    print("¡PAGO APROBADO!")
                    pedido = transaccion.pedido
                    pedido.estado = 'procesando'
                    pedido.save()
                    
                    # Limpiar el carrito
                    if 'cart' in request.session:
                        del request.session['cart']
                    
                    messages.success(request, '¡Pago realizado exitosamente con Mercado Pago!')
                    
                    context = {
                        'pedido': pedido,
                        'transaccion': transaccion,
                        'exito': True,
                        'response': payment_data,
                        'es_mercadopago': True
                    }
                    return render(request, 'store/confirmacion_pago.html', context)
                
                elif payment_data.get('status') in ['rejected', 'cancelled']:
                    print(f"PAGO {payment_data.get('status').upper()}")
                    pedido = transaccion.pedido
                    pedido.estado = 'cancelado'
                    pedido.save()
                    
                    # Restaurar stock
                    for detalle in pedido.detalles.all():
                        producto = detalle.producto
                        producto.stock += detalle.cantidad
                        producto.save()
                    
                    messages.error(request, 'El pago fue rechazado. Por favor, intenta nuevamente.')
                    
                    context = {
                        'pedido': pedido,
                        'transaccion': transaccion,
                        'exito': False,
                        'response': payment_data,
                        'es_mercadopago': True
                    }
                    return render(request, 'store/confirmacion_pago.html', context)
                
                else:  # pending, in_process, etc.
                    print(f"PAGO EN ESTADO: {payment_data.get('status')}")
                    messages.info(request, 'Tu pago está siendo procesado. Te notificaremos cuando se confirme.')
                    return redirect('home')
        
        # Si no hay payment_id pero hay status
        elif status:
            transaccion.estado = status
            transaccion.save()
            
            if status == 'approved':
                pedido = transaccion.pedido
                pedido.estado = 'procesando'
                pedido.save()
                
                if 'cart' in request.session:
                    del request.session['cart']
                
                messages.success(request, '¡Pago realizado exitosamente!')
                return redirect('generar_recibo_pdf', pedido_id=pedido.id)
            else:
                messages.warning(request, 'El pago no se completó correctamente.')
                return redirect('checkout')
        
    except Exception as e:
        print(f"Error en retorno Mercado Pago: {e}")
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

# =========================================
# VISTA PRINCIPAL DE MÉTRICAS
# =========================================

@admin_required
# @user_passes_test... (si usas este decorador también, mantenlo)
@admin_required
def ver_metricas(request):
    now = timezone.now()
    
    # 1. Definir rangos de fechas
    hace_una_semana = now - datetime.timedelta(days=7)
    hace_un_mes = now - datetime.timedelta(days=30)
    hace_un_ano = now - datetime.timedelta(days=365)
    
    # --- CORRECCIÓN AQUÍ: Usamos datetime.timezone.utc ---
    inicio_de_los_tiempos = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)

    # 2. Generar datos para cada período usando las funciones auxiliares
    metrics_data = {
        'weekly': {
            'sales_over_time': obtener_ventas_en_tiempo(hace_una_semana, TruncDay),
            'shipping': obtener_metricas_envio(hace_una_semana),
            'top_products': obtener_top_productos(hace_una_semana)
        },
        'monthly': {
            'sales_over_time': obtener_ventas_en_tiempo(hace_un_mes, TruncDay),
            'shipping': obtener_metricas_envio(hace_un_mes),
            'top_products': obtener_top_productos(hace_un_mes)
        },
        'yearly': {
            'sales_over_time': obtener_ventas_en_tiempo(hace_un_ano, TruncMonth),
            'shipping': obtener_metricas_envio(hace_un_ano),
            'top_products': obtener_top_productos(hace_un_ano)
        },
        'all_time': {
            'sales_over_time': obtener_ventas_en_tiempo(inicio_de_los_tiempos, TruncYear),
            'shipping': obtener_metricas_envio(inicio_de_los_tiempos),
            'top_products': obtener_top_productos(inicio_de_los_tiempos)
        }
    }

    return render(request, 'gestion/metrics.html', {'metrics_data': metrics_data})

def subir_comprobante(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Evitar que suban comprobantes a pedidos que no son de transferencia o ya pagados
    if pedido.estado != 'procesando' and pedido.estado != 'pendiente': # Ajusta según tus estados iniciales
         messages.error(request, 'Este pedido no requiere subida de comprobantes actualmente.')
         return redirect('home')

    # Verificar si ya existe un pago en revisión
    if hasattr(pedido, 'pago_transferencia'):
        if pedido.pago_transferencia.estado == 'PENDIENTE':
             messages.info(request, 'Ya has subido un comprobante para este pedido. Está en revisión.')
             return redirect('home') # O a una página de "gracias"

    if request.method == 'POST':
        form = ComprobantePagoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Crear el registro de PagoTransferencia
                    pago_transferencia = PagoTransferencia.objects.create(
                        pedido=pedido,
                        comentario_usuario=form.cleaned_data['comentario'],
                        estado='PENDIENTE'
                    )
                    
                    # 2. Guardar cada imagen subida (se van directo a Azure por el modelo)
                    imagenes = request.FILES.getlist('imagenes')
                    for imagen in imagenes:
                        ComprobanteTransferencia.objects.create(
                            pago=pago_transferencia,
                            imagen=imagen
                        )
                    
                    # 3. Actualizar estado del pedido (opcional, para indicar que espera revisión)
                    # pedido.estado = 'esperando_validacion' 
                    # pedido.save()

                messages.success(request, 'Comprobante subido exitosamente. Te notificaremos cuando sea aprobado.')
                return redirect('generar_recibo_pdf', pedido_id=pedido.id)

            except Exception as e:
                print(f"Error al subir comprobantes: {e}")
                messages.error(request, 'Hubo un error al guardar tus comprobantes. Intenta de nuevo.')
    else:
        form = ComprobantePagoForm()

    # Datos de cuentas bancarias ficticias
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
                
            messages.warning(request, f'Pago del pedido #{pago.pedido.id} RECHAZADO y stock restaurado.')
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
        print(f"Error al cancelar pedido {pedido_id}: {e}")
        messages.error(request, 'Hubo un error al intentar cancelar el pedido.')

    return redirect('home') 