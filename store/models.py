from django.db import models
from django.core.validators import MinValueValidator
from .validators import validate_chilean_phone, validate_name, validate_email_extended, validate_chilean_rut
from .image_utils import optimize_product_image, optimize_additional_image, optimize_comprobante_image  # AGREGAR optimize_comprobante_image
import os
import random
import string
from django.core.validators import MinValueValidator, MaxValueValidator 
from decimal import Decimal 
from django.utils import timezone
import datetime

# =========================================
# FUNCIONES AUXILIARES
# =========================================

def generate_tracking_number():
    """Genera un código aleatorio de 8 DÍGITOS (solo números)"""
    # CAMBIO AQUÍ: Usamos solo string.digits
    return ''.join(random.choices(string.digits, k=8))

def transferencia_upload_path(instance, filename):
    """Define la ruta de subida para comprobantes: transferencias/ID_PEDIDO/archivo"""
    return f'transferencias/{instance.pago.pedido.id}/{filename}'

# =========================================
# MODELOS BASE (INDEPENDIENTES)
# =========================================

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    es_marca_auto = models.BooleanField(default=False, verbose_name="Es Marca de Auto", help_text="Marcar si esta marca corresponde a un fabricante de vehículos (ej: Nissan, Toyota).")

    def __str__(self):
        return self.nombre


class Tag(models.Model):
    """
    Modelo para etiquetas/tags de productos.
    Permite categorización adicional y mejora el SEO.
    """
    nombre = models.CharField(
        max_length=50, 
        unique=True,
        help_text='Nombre de la etiqueta (ej: "bluetooth", "gps", "android")'
    )
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = models.CharField(
        max_length=7, 
        default='#6a0dad',
        help_text='Color hexadecimal para mostrar el tag (ej: #6a0dad)'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Auto-generar slug si no existe
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

# =========================================
# MODELOS DE PRODUCTO
# =========================================

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    descuento = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name="Porcentaje de Oferta (0-99%)"
    )
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_pub = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True, related_name='productos', verbose_name='Etiquetas')  # NUEVO
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Optimizar imagen principal antes de guardar
        if self.imagen and hasattr(self.imagen, 'file'):
            self.imagen = optimize_product_image(self.imagen)
        
        if self.stock == 0:
            self.activo = False
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        """Retorna lista de nombres de tags para SEO"""
        return [tag.nombre for tag in self.tags.all()]
    
    def get_tags_display(self):
        """Retorna tags como string separado por comas"""
        return ', '.join(self.get_tags_list())
        
    @property
    def precio_oferta(self):
        """Calcula el precio con el descuento base aplicado (para Webpay/otros)"""
        if self.descuento > 0:
            descuento_decimal = Decimal(self.descuento) / Decimal(100)
            precio_final = self.precio * (1 - descuento_decimal)
            return int(precio_final)
        return int(self.precio)
    
    @property
    def precio_transferencia(self):
        """
        Calcula el precio final para transferencia.
        Aplica el 3% EXTRA sobre el precio que ya tiene oferta (si existe).
        """
        base = self.precio_oferta
        precio_final = base * Decimal('0.97')
        return int(precio_final) # Redondeo a entero para CLP

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
    
    def save(self, *args, **kwargs):
        # Optimizar imagen adicional antes de guardar
        if self.imagen and hasattr(self.imagen, 'file'):
            self.imagen = optimize_additional_image(self.imagen)
        super().save(*args, **kwargs)


class Comentario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='comentarios')
    cliente = models.ForeignKey("Cliente", on_delete=models.CASCADE, null=True)
    contenido = models.TextField()
    estrellas = models.IntegerField(default=5)
    fecha = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False, help_text="Marcar si el comentario es público")

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        estado = "Aprobado" if self.aprobado else "Pendiente"
        return f'Comentario de {self.cliente.nombre} en {self.producto.nombre} ({estado})'

# =========================================
# MODELOS DE USUARIO (CLIENTE / EMPLEADO)
# =========================================

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
    is_superadmin = models.BooleanField(default=False)

    class Meta:
        db_table = 'EMPLEADOS'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.cargo})"

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

class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    calle = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=200)
    region = models.CharField(max_length=200)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"

# =========================================
# MODELOS DE PEDIDO Y NOTIFICACIONES
# =========================================

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    METODO_PAGO_CHOICES = [
        ('webpay', 'Webpay Plus'),
        ('mercadopago', 'Mercado Pago'),
        ('transferencia', 'Transferencia Bancaria'),
        ('otro', 'Otro'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='otro')
    tracking_number = models.CharField(max_length=8, unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            new_tracking = generate_tracking_number()
            while Pedido.objects.filter(tracking_number=new_tracking).exists():
                new_tracking = generate_tracking_number()
            self.tracking_number = new_tracking
        super().save(*args, **kwargs)

    def __str__(self):
        cliente_nombre = self.cliente.nombre if self.cliente else 'Cliente Desconocido'
        tracking = self.tracking_number if self.tracking_number else f"ID {self.id}"
        return f"Pedido #{tracking} - {cliente_nombre}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

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

# =========================================
# MODELOS DE PAGO (TRANSACTIONALES)
# =========================================

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
    
    response_code = models.CharField(max_length=10, blank=True, null=True, help_text='Código de respuesta')
    authorization_code = models.CharField(max_length=10, blank=True, null=True, help_text='Código de autorización')
    payment_type_code = models.CharField(max_length=10, blank=True, null=True, help_text='Tipo de pago')
    card_number = models.CharField(max_length=20, blank=True, null=True, help_text='Últimos 4 dígitos de la tarjeta')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transacción Webpay'
        verbose_name_plural = 'Transacciones Webpay'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Transacción {self.buy_order} - {self.estado}"

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
    
    status_detail = models.CharField(max_length=100, blank=True, null=True, help_text='Detalle del estado')
    payment_method_id = models.CharField(max_length=50, blank=True, null=True, help_text='Método de pago')
    payment_type_id = models.CharField(max_length=50, blank=True, null=True, help_text='Tipo de pago')
    card_last_four_digits = models.CharField(max_length=4, blank=True, null=True, help_text='Últimos 4 dígitos')
    
    payer_email = models.EmailField(blank=True, null=True, help_text='Email del pagador')
    payer_identification = models.CharField(max_length=50, blank=True, null=True, help_text='Identificación')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True, help_text='Fecha de aprobación')
    
    class Meta:
        verbose_name = 'Transacción Mercado Pago'
        verbose_name_plural = 'Transacciones Mercado Pago'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"MP-{self.preference_id[:8]} - {self.estado}"

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
        return f"Transferencia Pedido #{self.pedido.tracking_number or self.pedido.id} - {self.estado}"

class ComprobanteTransferencia(models.Model):
    pago = models.ForeignKey(PagoTransferencia, on_delete=models.CASCADE, related_name='comprobantes')
    imagen = models.ImageField(upload_to=transferencia_upload_path)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comprobante {self.id} para Pedido #{self.pago.pedido.tracking_number or self.pago.pedido.id}"
    
    def save(self, *args, **kwargs):
        # Optimizar comprobante antes de guardar
        if self.imagen and hasattr(self.imagen, 'file'):
            self.imagen = optimize_comprobante_image(self.imagen)
        super().save(*args, **kwargs)

class PasswordResetToken(models.Model):
    """Tokens para recuperación de contraseña"""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    
    def is_valid(self):
        """Verifica si el token sigue siendo válido (1 hora de validez)"""
        expiracion = self.fecha_creacion + datetime.timedelta(hours=1)
        return not self.usado and timezone.now() < expiracion
    
    @staticmethod
    def generate_token():
        """Genera un token aleatorio único"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    
    class Meta:
        db_table = 'PASSWORD_RESET_TOKENS'
    
    def __str__(self):
        return f"Token para {self.cliente.email}"
    


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-fecha']

    def __str__(self):
        return f"Mensaje de {self.nombre} ({self.email})"