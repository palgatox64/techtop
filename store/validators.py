import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email

def validate_chilean_rut(rut):
    """
    Valida el formato y dígito verificador del RUT chileno.
    Formato esperado: 12345678-9 o 12.345.678-9
    """
    
    rut_limpio = rut.replace('.', '').replace('-', '').upper()
    
    
    if not re.match(r'^\d{7,8}[0-9K]$', rut_limpio):
        raise ValidationError('Formato de RUT inválido. Use el formato: 12345678-9')
    
    
    numero = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]
    
    
    suma = 0
    multiplicador = 2
    
    for digito in reversed(numero):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    
    if dv_ingresado != dv_calculado:
        raise ValidationError(f'RUT inválido. El dígito verificador correcto es {dv_calculado}')

def validate_chilean_phone(phone):
    """Valida que el teléfono sea formato chileno (9 dígitos comenzando con 9)"""
    if not re.match(r'^9\d{8}$', phone):
        raise ValidationError('El número de teléfono debe tener 9 dígitos y comenzar con 9.')

def validate_name(name):
    """Valida que el nombre solo contenga letras y espacios"""
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', name):
        raise ValidationError('El nombre solo debe contener letras y espacios.')
    
    if len(name) < 2:
        raise ValidationError('El nombre debe tener al menos 2 caracteres.')

def validate_strong_password(password):
    """Valida que la contraseña sea segura con caracteres especiales más amplios"""
    if len(password) < 8:
        raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    
    if not re.search(r'\d', password):
        raise ValidationError('La contraseña debe contener al menos un número.')
    
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?~`]', password):
        raise ValidationError('La contraseña debe contener al menos un carácter especial.')
    
    
    forbidden_chars = re.search(r'[\'"\\]', password)
    if forbidden_chars:
        raise ValidationError('La contraseña no puede contener comillas o barras invertidas.')

def validate_email_extended(email):
    """Validación extendida de email"""
    
    django_validate_email(email)
    
    
    if len(email) > 100:
        raise ValidationError('El correo electrónico es demasiado largo.')
