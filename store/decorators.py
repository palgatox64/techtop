from django.shortcuts import redirect
from django.contrib import messages
from .models import Empleado

def admin_required(view_func):
    """
    Decorador que verifica si el usuario es un empleado activo con sesión iniciada.
    """
    def _wrapped_view(request, *args, **kwargs):
        
        if 'empleado_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión como empleado para acceder a esta página.')
            return redirect('login')
        
        try:
            
            empleado = Empleado.objects.get(id_empleado=request.session['empleado_id'])
            if not empleado.activo:
                messages.error(request, 'Tu cuenta de empleado ha sido desactivada.')
                request.session.flush()
                return redirect('login')
        except Empleado.DoesNotExist:
            messages.error(request, 'Sesión inválida. Por favor, inicia sesión de nuevo.')
            request.session.flush()
            return redirect('login')

        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def superadmin_required(view_func):
    """
    Decorador que verifica si el usuario es un empleado activo, con sesión iniciada
    Y ADEMÁS tiene permisos de superadministrador.
    """
    def _wrapped_view(request, *args, **kwargs):
        
        if 'empleado_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión como empleado para acceder a esta página.')
            return redirect('login')
        
        try:
            
            empleado = Empleado.objects.get(id_empleado=request.session['empleado_id'])
            if not empleado.activo:
                messages.error(request, 'Tu cuenta de empleado ha sido desactivada.')
                request.session.flush()
                return redirect('login')
            
            if not empleado.is_superadmin:
                messages.error(request, 'No tienes permisos de superadministrador para acceder a esta página.')
                return redirect('panel_gestion') 

        except Empleado.DoesNotExist:
            messages.error(request, 'Sesión inválida. Por favor, inicia sesión de nuevo.')
            request.session.flush()
            return redirect('login')

        
        return view_func(request, *args, **kwargs)
    return _wrapped_view