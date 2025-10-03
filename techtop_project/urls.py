from django.contrib import admin
from django.urls import path
from store.views import home, contacto # Asegúrate de importar la vista

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), # Añade esta línea para la página de inicio
    path('contacto/', contacto, name='contacto'), # Añade esta línea para la página de contacto
]