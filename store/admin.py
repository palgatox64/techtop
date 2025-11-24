from django.contrib import admin
from .models import Categoria, Marca, Producto, Cliente, Direccion, Pedido, DetallePedido, ImagenProducto, Empleado, Tag

# Define el 'inline' para las imágenes adicionales
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1 # Cuántos campos de subida de imagen extra mostrar por defecto

# Personaliza cómo se ve el admin de Producto
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'marca', 'get_tags_display')
    inlines = [ImagenProductoInline]
    filter_horizontal = ('tags',)  # Widget mejorado para selección de tags

class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'email', 'cargo', 'activo', 'fecha_contratacion')
    list_filter = ('activo', 'cargo', 'fecha_contratacion')
    search_fields = ('nombre', 'apellidos', 'email')
    ordering = ('-fecha_contratacion',)

admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente)
admin.site.register(Direccion)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(Tag)
