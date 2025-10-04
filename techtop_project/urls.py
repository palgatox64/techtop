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
    product_detail,
    add_to_cart,
    view_cart,
    update_cart,
    remove_from_cart,
    radios_catalog,
    product_catalog,
    login_view, 
    register_view 
)

from django.conf import settings
from django.conf.urls.static import static

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
    path('radios/', radios_catalog, name='radios_catalog'),
    path('producto/<int:product_id>/', product_detail, name='product_detail'),
    path('carro/', view_cart, name='view_cart'),
    path('agregar/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('actualizar-carro/<int:product_id>/', update_cart, name='update_cart'),
    path('eliminar-del-carro/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)