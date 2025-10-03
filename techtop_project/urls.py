from django.contrib import admin
from django.urls import path
from store.views import home, contacto, about 
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('contacto/', contacto, name='contacto'), 
    path('quienes-somos/', about, name='about'), 
]