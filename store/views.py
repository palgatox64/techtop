from django.shortcuts import render, redirect
from .models import Producto, Marca
from django.db.models import Count
from django.contrib.auth.hashers import make_password 
from django.contrib import messages 
from .models import Cliente 
import re 
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password 
from django.http import JsonResponse 

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
    
    context = {
        'products': products,
        'available_brands': available_brands,
        'selected_brand': brand_name,
        'selected_brands_from_form': selected_brands,
    }
    
    return render(request, 'store/tienda.html', context)

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        correo = request.POST.get('email')
        password = request.POST.get('password')
        print(f">>> Intento de login con correo: {correo}") 

        try:
            cliente = Cliente.objects.get(email=correo)
            
            if check_password(password, cliente.pass_hash):
                print(f">>> Contraseña correcta para {correo}. Iniciando sesión.")
                
                request.session['cliente_id'] = cliente.id_cliente
                request.session['cliente_nombre'] = cliente.nombre
                
                return JsonResponse({
                    'success': True, 
                    'message': f'¡Bienvenido de vuelta, {cliente.nombre}!', 
                    'redirect_url': '/'
                })
            else:
                print(f">>> Contraseña INCORRECTA para {correo}.")
                return JsonResponse({
                    'success': False, 
                    'message': 'Correo o contraseña incorrectos.'
                })

        except Cliente.DoesNotExist:
            print(f">>> No se encontró ningún usuario con el correo {correo}.")
            return JsonResponse({
                'success': False, 
                'message': 'Correo o contraseña incorrectos.'
            })
        except Exception as e:
            print(f">>> Error inesperado en login: {e}")
            return JsonResponse({
                'success': False, 
                'message': 'Ocurrió un error inesperado. Intenta de nuevo.'
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