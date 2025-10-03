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
    terminos_condiciones,
    product_catalog,
    login_view, 
    register_view 
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
    path('tienda/', product_catalog, name='product_catalog'),
    path('tienda/marca/<str:brand_name>/', product_catalog, name='product_catalog_by_brand'),
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='register'),
]