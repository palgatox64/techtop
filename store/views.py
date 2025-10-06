from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Marca, Categoria
from django.db.models import Count
from django.contrib.auth.hashers import make_password 
from django.contrib import messages 
from .models import Cliente 
import re 
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password 
from django.http import JsonResponse 
from decimal import Decimal

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
    if selected_brands:
        products = products.filter(marca__nombre__in=selected_brands)
    available_brands = Marca.objects.filter(
        producto__categoria__nombre='RADIO ANDROID' 
    ).annotate(
        product_count=Count('producto')
    ).filter(product_count__gt=0).order_by('nombre')
    
    for product in products:
        product.precio_secundario = product.precio * Decimal('1.07')

    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brands_from_form': selected_brands,
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
        product.precio_secundario = product.precio * Decimal('1.07')
    
    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brand': brand_name,
        'selected_brands_from_form': selected_brands,
    }
    
    return render(request, 'store/tienda.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    precio_secundario = product.precio * Decimal('1.07')
    descuento_porcentaje = 0
    if precio_secundario > product.precio:
        descuento_porcentaje = round((1 - (product.precio / precio_secundario)) * 100)
    context = {
        'product': product,
        'precio_secundario': precio_secundario,
        'descuento_porcentaje': descuento_porcentaje,
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
        precio_secundario = product.precio * Decimal('1.07')

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal_transferencia': product.precio * quantity,
            'subtotal_otros_medios': precio_secundario * quantity,
        })
        total_transferencia += product.precio * quantity
        total_otros_medios += precio_secundario * quantity

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
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        correo = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            cliente = Cliente.objects.get(email=correo)
            
            if check_password(password, cliente.pass_hash):
                request.session['cliente_id'] = cliente.id_cliente
                request.session['cliente_nombre'] = cliente.nombre
                request.session['tipo_usuario'] = cliente.tipo_usuario
                

                return JsonResponse({
                    'success': True,
                    'message': f'¡Bienvenido de vuelta, {cliente.nombre}!',
                    'redirect_url': '/'
                })
                    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Correo o contraseña incorrectos.'
            })

def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':
        print(">>> Petición POST recibida en register_view.")

        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        print(f">>> Datos recibidos: Correo={correo}, Nombre={nombre}")

        if Cliente.objects.filter(email=correo).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            print(">>> ERROR DE VALIDACIÓN: El correo ya existe.")
            return redirect('register')

        if password != password2:
            messages.error(request, '¡Las contraseanzas no coinciden!')
            print(">>> ERROR DE VALIDACIÓN: Las contraseñas no coinciden.")
            return redirect('register')

        if not re.match(r'^(?=.*[A-Z])(?=.*\d).{8,}$', password):
            messages.error(request, 'La contraseña no es segura (mín. 8 caracteres, 1 mayúscula, 1 número).')
            print(">>> ERROR DE VALIDACIÓN: La contraseña no es segura.")
            return redirect('register')
        
        if not re.match(r'^\d{9}$', telefono):
            messages.error(request, 'El número de teléfono debe tener exactamente 9 dígitos.')
            print(">>> ERROR DE VALIDACIÓN: El teléfono es inválido.")
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

            print(">>> Intentando ejecutar .save() en la base de datos...")
            nuevo_cliente.save()
            
            print(">>> ¡ÉXITO! .save() se ejecutó sin errores.")
            messages.success(request, '¡Tu cuenta ha sido creada con éxito! Ya puedes iniciar sesión.')
            return redirect('login')
        
        except Exception as e:
            print(f"!!!!!!!!!! OCURRIÓ UN ERROR AL GUARDAR EN LA BASE DE DATOS !!!!!!!!!!")
            print(f"El error específico es: {e}")
            messages.error(request, 'Ocurrió un error inesperado al crear tu cuenta. Contacta a soporte.')
            return redirect('register')

def logout_view(request):
    if 'cliente_id' in request.session:
        try:
            request.session.flush()
            messages.success(request, 'Has cerrado sesión exitosamente.')
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")
            messages.error(request, 'Ocurrió un error al cerrar sesión.')
    
    return redirect('home')