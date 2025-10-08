from django.contrib import admin
from .models import Categoria, Marca, Producto, Cliente, Direccion, Pedido, DetallePedido, ImagenProducto

# Define el 'inline' para las imágenes adicionales
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1 # Cuántos campos de subida de imagen extra mostrar por defecto

# Personaliza cómo se ve el admin de Producto
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'marca')
    inlines = [ImagenProductoInline] # Añade el inline aquí

admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente)
admin.site.register(Direccion)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
