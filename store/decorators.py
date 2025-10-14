from django.shortcuts import redirect
from django.contrib import messages
from .models import Empleado

def admin_required(view_func):
    """
    Decorador que verifica si el usuario es un empleado activo con sesión iniciada.
    """
    def _wrapped_view(request, *args, **kwargs):
        # 1. Verificar si hay sesión de empleado
        if 'empleado_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión como empleado para acceder a esta página.')
            return redirect('login')
        
        try:
            # 2. Obtener el empleado y verificar que esté activo
            empleado = Empleado.objects.get(id_empleado=request.session['empleado_id'])
            if not empleado.activo:
                messages.error(request, 'Tu cuenta de empleado ha sido desactivada.')
                request.session.flush()
                return redirect('login')
        except Empleado.DoesNotExist:
            messages.error(request, 'Sesión inválida. Por favor, inicia sesión de nuevo.')
            request.session.flush()
            return redirect('login')

        # Si todo está en orden, permite el acceso a la vista
        return view_func(request, *args, **kwargs)
    return _wrapped_view