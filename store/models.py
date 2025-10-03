from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    imagen_url = models.URLField(max_length=200)
    fecha_pub = models.DateField(auto_now_add=True)
    
    # Relaciones (Foreign Keys)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.nombre

# --- Modelo para la tabla CLIENTES (según tu DDL) ---
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)  # NUMERIC(10) NOT NULL PRIMARY KEY
    nombre = models.CharField(max_length=100)        # VARCHAR(100) NOT NULL
    apellidos = models.CharField(max_length=150)     # VARCHAR(150) NOT NULL  
    email = models.EmailField(max_length=100, unique=True)  # VARCHAR(100) NOT NULL UNIQUE
    pass_hash = models.CharField(max_length=200)     # VARCHAR(200) NOT NULL
    telefono = models.CharField(max_length=9)            # VARCHAR(9) NOT NULL

    class Meta:
        # Usar el nombre estándar de Django: store_cliente
        pass
        
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

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