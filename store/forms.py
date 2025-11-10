from django import forms
from .models import Categoria, Marca, Producto, Comentario
from django.core.exceptions import ValidationError 
from .models import Cliente, Direccion # Asegúrate de importar los modelos

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido', 'estrellas']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu reseña aquí...'
            }),
            'estrellas': forms.HiddenInput(attrs={'id': 'estrellas-input'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Radios para Auto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Una breve descripción...'}),
        }

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sony'}),
        }

class ProductoForm(forms.ModelForm):
    publicar_redes = forms.BooleanField(
        required=False,
        initial=True,
        label='¿Publicar en redes sociales?',
        help_text='Si está marcado, el producto se compartirá automáticamente en Facebook e Instagram'
    )
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen', 'categoria', 'marca', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'activo': 'Producto Activo (visible en tienda)',
        }

class CheckoutForm(forms.Form):
    # DATOS DE CONTACTO
    nombre = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'}))
    apellidos = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Tus apellidos'}))
    rut = forms.CharField(max_length=12, required=True, widget=forms.TextInput(attrs={'placeholder': '12.345.678-9'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}))
    telefono = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'placeholder': '987654321'}))

    # TIPO DE ENTREGA
    DELIVERY_CHOICES = [
        ('delivery', 'Delivery a Domicilio'),
        ('retiro', 'Retiro en Tienda'),
    ]
    tipo_entrega = forms.ChoiceField(
        choices=DELIVERY_CHOICES, 
        widget=forms.RadioSelect, 
        initial='delivery',
        required=True
    )

    # --- NUEVOS CAMPOS DE DIRECCIÓN (ocultos al inicio) ---
    TIPO_VIVIENDA_CHOICES = [
        ('casa', 'Casa'),
        ('depto', 'Departamento'),
    ]
    calle = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nombre de la calle o avenida'}))
    numero = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Ej: 1234'}))
    tipo_vivienda = forms.ChoiceField(choices=TIPO_VIVIENDA_CHOICES, required=False, widget=forms.Select)
    depto_pasaje = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'N° de Depto, Pasaje, Villa, etc.'}))
    codigo_postal = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'placeholder': 'Opcional'}))


    # MÉTODO DE PAGO
    PAYMENT_CHOICES = [
        ('webpay', 'Webpay Plus'),
        ('mercadopago', 'Mercado Pago'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    metodo_pago = forms.ChoiceField(
        choices=PAYMENT_CHOICES, 
        widget=forms.RadioSelect, 
        initial='webpay',
        required=True
    )

    # --- LÓGICA DE VALIDACIÓN ---
    def clean(self):
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get('tipo_entrega')

        if tipo_entrega == 'delivery':
            # Si es delivery, estos campos son obligatorios
            calle = cleaned_data.get('calle')
            numero = cleaned_data.get('numero')
            tipo_vivienda = cleaned_data.get('tipo_vivienda')

            if not calle:
                self.add_error('calle', 'La calle es obligatoria para el delivery.')
            if not numero:
                self.add_error('numero', 'El número es obligatorio para el delivery.')
            if not tipo_vivienda:
                self.add_error('tipo_vivienda', 'Debes seleccionar un tipo de vivienda.')
        
        return cleaned_data
    
# Widget personalizado para permitir múltiples archivos
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ComprobantePagoForm(forms.Form):
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Ej: Pago realizado desde cuenta RUT de Juan Pérez...'
        }),
        label="Comentario adicional (Opcional)"
    )
    imagenes = MultipleFileField(
        label="Subir Comprobantes (Puedes seleccionar varias)",
        widget=MultipleFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
class PerfilUsuarioForm(forms.Form):
    # Datos del Cliente
    nombre = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidos = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'})) # Email suele ser solo lectura para no romper login
    telefono = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Datos de Dirección (Opcionales si no ha comprado, pero buenos para tener)
    calle = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    ciudad = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    region = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))