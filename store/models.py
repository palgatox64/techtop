from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_chilean_phone, validate_name, validate_email_extended, validate_chilean_rut
import os

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
        if self.cliente:
            return f"Pedido #{self.id} de {self.cliente.nombre} {self.cliente.apellidos}"
        return f"Pedido #{self.id} (Cliente Desconocido)"
    METODO_PAGO_CHOICES = [
        ('webpay', 'Webpay Plus'),
        ('mercadopago', 'Mercado Pago'),
        ('transferencia', 'Transferencia Bancaria'),
        ('otro', 'Otro'),
    ]
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='otro')
    
class Notificacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificaciones')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True, blank=True)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Notificación para {self.cliente.nombre} - {self.fecha_creacion}"

# --- Modelo para la tabla DETALLES_PEDIDO ---
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

# --- Modelo para transacciones de Webpay ---
class TransaccionWebpay(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('AUTORIZADO', 'Autorizado'),
        ('RECHAZADO', 'Rechazado'),
        ('ANULADO', 'Anulado'),
    ]
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='transacciones_webpay')
    token = models.CharField(max_length=255, unique=True, help_text='Token generado por Transbank')
    buy_order = models.CharField(max_length=100, unique=True, help_text='Orden de compra única')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    # Datos de respuesta de Transbank
    response_code = models.CharField(max_length=10, blank=True, null=True, help_text='Código de respuesta')
    authorization_code = models.CharField(max_length=10, blank=True, null=True, help_text='Código de autorización')
    payment_type_code = models.CharField(max_length=10, blank=True, null=True, help_text='Tipo de pago')
    card_number = models.CharField(max_length=20, blank=True, null=True, help_text='Últimos 4 dígitos de la tarjeta')
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transacción Webpay'
        verbose_name_plural = 'Transacciones Webpay'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Transacción {self.buy_order} - {self.estado}"

# --- Modelo para transacciones de Mercado Pago ---
class TransaccionMercadoPago(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('authorized', 'Autorizado'),
        ('in_process', 'En Proceso'),
        ('in_mediation', 'En Mediación'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
        ('charged_back', 'Contracargo'),
    ]
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='transacciones_mercadopago')
    preference_id = models.CharField(max_length=255, unique=True, help_text='ID de preferencia de MercadoPago')
    payment_id = models.CharField(max_length=255, blank=True, null=True, help_text='ID del pago confirmado')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')
    
    # Datos de respuesta de MercadoPago
    status_detail = models.CharField(max_length=100, blank=True, null=True, help_text='Detalle del estado')
    payment_method_id = models.CharField(max_length=50, blank=True, null=True, help_text='Método de pago')
    payment_type_id = models.CharField(max_length=50, blank=True, null=True, help_text='Tipo de pago')
    card_last_four_digits = models.CharField(max_length=4, blank=True, null=True, help_text='Últimos 4 dígitos')
    
    # Datos del pagador
    payer_email = models.EmailField(blank=True, null=True, help_text='Email del pagador')
    payer_identification = models.CharField(max_length=50, blank=True, null=True, help_text='Identificación')
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True, help_text='Fecha de aprobación')
    
    class Meta:
        verbose_name = 'Transacción Mercado Pago'
        verbose_name_plural = 'Transacciones Mercado Pago'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"MP-{self.preference_id[:8]} - {self.estado}"

# --- FUNCIÓN PARA LA RUTA DE AZURE ---
def transferencia_upload_path(instance, filename):
    # Esta función define la ruta: transferencias/ID_PEDIDO/nombre_archivo
    return f'transferencias/{instance.pago.pedido.id}/{filename}'

# --- NUEVOS MODELOS AL FINAL DEL ARCHIVO ---

class PagoTransferencia(models.Model):
    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('APROBADO', 'Pago Aprobado'),
        ('RECHAZADO', 'Pago Rechazado'),
    ]
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago_transferencia')
    comentario_usuario = models.TextField(blank=True, null=True, help_text="Comentario dejado por el cliente")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE')
    fecha_revision = models.DateTimeField(null=True, blank=True)
    comentario_admin = models.TextField(blank=True, null=True, help_text="Comentario interno del administrador")

    def __str__(self):
        return f"Transferencia Pedido #{self.pedido.id} - {self.estado}"

class ComprobanteTransferencia(models.Model):
    pago = models.ForeignKey(PagoTransferencia, on_delete=models.CASCADE, related_name='comprobantes')
    imagen = models.ImageField(upload_to=transferencia_upload_path)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comprobante {self.id} para Pedido #{self.pago.pedido.id}"