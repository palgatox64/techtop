from django.contrib import admin
from .models import Categoria, Marca, Producto, Cliente, Direccion, Pedido, DetallePedido

admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Direccion)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
