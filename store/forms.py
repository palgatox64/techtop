from django import forms
from .models import Categoria, Marca, Producto, Comentario
from django.core.exceptions import ValidationError 
from .models import Cliente, Direccion 


class ComentarioForm(forms.ModelForm):
    estrellas = forms.ChoiceField(
        choices=[(5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1')],
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),
        initial=5
    )
    
    class Meta:
        model = Comentario
        fields = ['contenido', 'estrellas']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu reseña aquí...'
            }),
        }
        labels = {
            'contenido': 'Tu opinión sobre el producto',
            'estrellas': 'Tu calificación (5 es excelente)'
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
        fields = ['nombre', 'descripcion', 'precio', 'descuento', 'stock', 'imagen', 'categoria', 'marca', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={
                'type': 'range',
                'class': 'form-range discount-slider', 
                'min': '0',
                'max': '99',
                'step': '1'
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'activo': 'Producto Activo (visible en tienda)',
            'descuento': 'Oferta Especial (%) - Arrastra para aplicar'
        }

class CheckoutForm(forms.Form):
    
    nombre = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'}))
    apellidos = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Tus apellidos'}))
    rut = forms.CharField(max_length=12, required=True, widget=forms.TextInput(attrs={'placeholder': '12.345.678-9'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}))
    telefono = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'placeholder': '987654321'}))

    
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

    
    TIPO_VIVIENDA_CHOICES = [
        ('casa', 'Casa'),
        ('depto', 'Departamento'),
    ]
    calle = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nombre de la calle o avenida'}))
    numero = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Ej: 1234'}))
    tipo_vivienda = forms.ChoiceField(choices=TIPO_VIVIENDA_CHOICES, required=False, widget=forms.Select)
    depto_pasaje = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'N° de Depto, Pasaje, Villa, etc.'}))
    codigo_postal = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'placeholder': 'Opcional'}))


    
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

    
    def clean(self):
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get('tipo_entrega')

        if tipo_entrega == 'delivery':
            
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
    
    nombre = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidos = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'})) 
    telefono = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    
    calle = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    ciudad = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    region = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

from .models import Empleado
from django.contrib.auth.hashers import make_password

class EmpleadoForm(forms.ModelForm):
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco para no cambiar'}),
        required=False,
        label="Contraseña"
    )

    class Meta:
        model = Empleado
        fields = ['rut', 'nombre', 'apellidos', 'email', 'telefono', 'cargo', 'activo', 'is_superadmin']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superadmin': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        labels = {
            'activo': 'Empleado Activo',
            'is_superadmin': 'Es Superadministrador',
            'rut': 'RUT (sin puntos, con guión)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            self.fields['password'].required = False
        else:
            
            self.fields['password'].required = True
            self.fields['password'].widget.attrs['placeholder'] = 'Contraseña (obligatoria)'

    def save(self, commit=True):
        empleado = super().save(commit=False)
        password = self.cleaned_data.get("password")
        
        
        if password:
            empleado.pass_hash = make_password(password)
        
        if commit:
            empleado.save()
        return empleado