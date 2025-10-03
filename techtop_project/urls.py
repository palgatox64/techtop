from django.contrib import admin
from django.urls import path
from store.views import (
    home, 
    contacto, 
    about, 
    seguimiento_compra, 
    centro_ayuda, 
    garantias, 
    politicas_privacidad, 
    terminos_condiciones
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('contacto/', contacto, name='contacto'), 
    path('quienes-somos/', about, name='about'),
    path('seguimiento-compra/', seguimiento_compra, name='seguimiento_compra'),
    path('centro-ayuda/', centro_ayuda, name='centro_ayuda'),
    path('garantias/', garantias, name='garantias'),
    path('politicas-privacidad/', politicas_privacidad, name='politicas_privacidad'),
    path('terminos-condiciones/', terminos_condiciones, name='terminos_condiciones'),
]