import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email

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
    
    # REGEX MÁS AMPLIA para caracteres especiales
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?~`]', password):
        raise ValidationError('La contraseña debe contener al menos un carácter especial.')
    
    # Opcional: Validar caracteres no permitidos por seguridad
    forbidden_chars = re.search(r'[\'\"\\]', password)
    if forbidden_chars:
        raise ValidationError('La contraseña no puede contener comillas simples, comillas dobles o barras invertidas.')

def validate_email_extended(email):
    """Validación extendida de email"""
    # Primero usar la validación estándar de Django
    django_validate_email(email)
    
    # Validaciones adicionales
    if len(email) > 100:
        raise ValidationError('El correo electrónico es demasiado largo.')
    
    # Verificar dominios comunes (comentado para ser menos restrictivo)
    # common_domains = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'live.com']
    # domain = email.split('@')[1].lower()
    # if domain not in common_domains:
    #     raise ValidationError(f'El dominio {domain} no está en la lista de dominios permitidos.')