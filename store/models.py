from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_chilean_phone, validate_name, validate_email_extended, validate_chilean_rut

# --- Modelo para la tabla CATEGORIAS ---
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.nombre

# --- Modelo para la tabla MARCAS ---
class Marca(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# --- Modelo para la tabla PRODUCTOS ---
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_pub = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    # Relaciones (Foreign Keys)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Desactivar automáticamente si el stock llega a 0
        if self.stock == 0:
            self.activo = False
        super().save(*args, **kwargs)

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name='imagenes_adicionales', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/adicionales/')
    orden = models.PositiveIntegerField(default=0, editable=False)
    descripcion = models.CharField(max_length=200, blank=True, null=True, help_text='Descripción opcional de la imagen')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'fecha_subida']
        verbose_name = 'Imagen adicional del producto'
        verbose_name_plural = 'Imágenes adicionales del producto'

    def __str__(self):
        return f"Imagen de {self.producto.nombre} (Orden: {self.orden})"

# --- Modelo para la tabla EMPLEADOS ---
class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True, validators=[validate_chilean_rut], help_text='Formato: 12345678-9')
    nombre = models.CharField(max_length=100, validators=[validate_name])
    apellidos = models.CharField(max_length=150, validators=[validate_name])
    email = models.EmailField(max_length=100, unique=True, validators=[validate_email_extended])
    pass_hash = models.CharField(max_length=200)
    telefono = models.CharField(max_length=9, validators=[validate_chilean_phone])
    cargo = models.CharField(max_length=100, default='Empleado')
    fecha_contratacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'EMPLEADOS'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.cargo})"

# --- Modelo para la tabla CLIENTES (CON RUT) ---
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True, validators=[validate_chilean_rut], help_text='Formato: 12345678-9')
    nombre = models.CharField(max_length=100, validators=[validate_name])
    apellidos = models.CharField(max_length=150, validators=[validate_name])
    email = models.EmailField(max_length=100, unique=True, validators=[validate_email_extended])
    pass_hash = models.CharField(max_length=200)
    telefono = models.CharField(max_length=9, validators=[validate_chilean_phone])

    class Meta:
        db_table = 'CLIENTES'

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.rut}"

# --- Modelo para la tabla DIRECCIONES ---
class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    calle = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=200)
    region = models.CharField(max_length=200)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"

# --- Modelo para la tabla PEDIDOS ---
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} de {self.cliente.nombre}"

# --- Modelo para la tabla DETALLES_PEDIDO ---
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"