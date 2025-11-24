from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
import re

register = template.Library()

@register.filter
def dot_thousands(value):
    """
    Convierte números a formato con puntos como separador de miles
    Ej: 200000 -> 200.000
    """
    if value is None:
        return value
    
    # Usar intcomma primero y luego reemplazar comas por puntos
    formatted = intcomma(value)
    return formatted.replace(',', '.')

@register.filter
def replace_dash(value):
    """
    Reemplaza guiones por espacios y formatea el texto
    """
    return value.replace('-', ' ')