from django.shortcuts import redirect
from django.contrib import messages
from .models import Cliente

def admin_required(view_func):
    """
    Decorador que verifica si el usuario ha iniciado sesión Y es un administrador.
    """
    def _wrapped_view(request, *args, **kwargs):
        # 1. Verificar si el usuario ha iniciado sesión
        if 'cliente_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login')
        
        try:
            # 2. Obtener el cliente y verificar si es administrador
            cliente = Cliente.objects.get(id_cliente=request.session['cliente_id'])
            if cliente.tipo_usuario != 'admin':
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('home')
        except Cliente.DoesNotExist:
            messages.error(request, 'Usuario no válido. Por favor, inicia sesión de nuevo.')
            return redirect('login')

        # Si todo está en orden, permite el acceso a la vista
        return view_func(request, *args, **kwargs)
    return _wrapped_view