from django.contrib import admin
from .models import Categoria, Marca, Producto, Cliente, Direccion, Pedido, DetallePedido, ImagenProducto, Empleado


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'marca')
    inlines = [ImagenProductoInline]

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