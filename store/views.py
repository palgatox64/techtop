from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Marca, Categoria
from django.db.models import Count, Q
from django.contrib.auth.hashers import make_password 
from django.contrib import messages 
from .models import Cliente, Empleado
import re 
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password 
from django.http import JsonResponse 
from decimal import Decimal
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .decorators import admin_required
from .forms import CategoriaForm, MarcaForm, ProductoForm
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
from django.db.models import Q 
from django.contrib.auth import logout

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
    products = Producto.objects.filter(categoria__nombre='RADIO ANDROID')
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
    products = Producto.objects.filter(categoria__nombre__in=electronics_categories)
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
    products = Producto.objects.filter(categoria__nombre__in=accessory_categories)
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
    products = Producto.objects.all()
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
    
    context = {
        'product': product,
        'precio_transferencia': precio_transferencia,
        'precio_normal': precio_normal,
        'descuento_porcentaje': descuento_porcentaje,
        'imagenes_adicionales': imagenes_adicionales,
    }
    return render(request, 'store/product_detail.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
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

        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        print(f">>> Datos recibidos: Correo={correo}, Nombre={nombre}")

        # Validaciones del backend
        
        # 1. Validar campos vacíos
        if not all([nombre, apellido, correo, telefono, password, password2]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        # 2. Validar formato de nombres (solo letras y espacios)
        name_regex = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(name_regex, nombre):
            messages.error(request, 'El nombre solo debe contener letras y espacios.')
            return redirect('register')
        
        if not re.match(name_regex, apellido):
            messages.error(request, 'El apellido solo debe contener letras y espacios.')
            return redirect('register')

        # 3. Validar longitud de nombres
        if len(nombre) < 2 or len(nombre) > 50:
            messages.error(request, 'El nombre debe tener entre 2 y 50 caracteres.')
            return redirect('register')
        
        if len(apellido) < 2 or len(apellido) > 100:
            messages.error(request, 'El apellido debe tener entre 2 y 100 caracteres.')
            return redirect('register')

        # 4. Validar formato de email
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, 'Formato de correo electrónico inválido.')
            return redirect('register')

        # 5. Validar longitud del email
        if len(correo) > 100:
            messages.error(request, 'El correo electrónico es demasiado largo.')
            return redirect('register')

        # 6. Verificar si el correo ya existe
        if Cliente.objects.filter(email=correo).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return redirect('register')

        # 7. Validar contraseñas coincidentes
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        # 8. Validar seguridad de contraseña (MÁS PERMISIVA CON CARACTERES ESPECIALES)
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
        
        # VALIDACIÓN MÁS AMPLIA DE CARACTERES ESPECIALES - AQUÍ ESTÁ EL CAMBIO PRINCIPAL
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?~`]', password):
            messages.error(request, 'La contraseña debe contener al menos un carácter especial.')
            return redirect('register')
        
        # Opcional: Evitar algunos caracteres problemáticos (puedes comentar esta línea si quieres permitir TODO)
        # if re.search(r'[\'\"\\]', password):
        #     messages.error(request, 'La contraseña no puede contener comillas simples, comillas dobles o barras invertidas.')
        #     return redirect('register')
        
        # 9. Validar teléfono chileno
        if not re.match(r'^9\d{8}$', telefono):
            messages.error(request, 'El número de teléfono debe tener 9 dígitos y comenzar con 9 (formato chileno).')
            return redirect('register')

        try:
            print(">>> Validaciones pasadas. Hasheando contraseña...")
            hashed_password = make_password(password)

            print(">>> Creando el objeto Cliente...")
            nuevo_cliente = Cliente(
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
            if 'UNIQUE constraint' in str(e) or 'unique' in str(e).lower():
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

    context = {
        'products': products,
        'search_query': query,
    }
    return render(request, 'store/search_results.html', context)