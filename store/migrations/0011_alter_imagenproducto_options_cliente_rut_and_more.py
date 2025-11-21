import datetime
import store.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_producto_activo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imagenproducto',
            options={'ordering': ['orden', 'fecha_subida'], 'verbose_name': 'Imagen adicional del producto', 'verbose_name_plural': 'Imágenes adicionales del producto'},
        ),
        migrations.AddField(
            model_name='cliente',
            name='rut',
            field=models.CharField(default='00000000-0', help_text='Formato: 12345678-9', max_length=12, unique=True, validators=[store.validators.validate_chilean_rut]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='empleado',
            name='rut',
            field=models.CharField(default='00000000-0', help_text='Formato: 12345678-9', max_length=12, unique=True, validators=[store.validators.validate_chilean_rut]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imagenproducto',
            name='descripcion',
            field=models.CharField(blank=True, help_text='Descripción opcional de la imagen', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='imagenproducto',
            name='fecha_subida',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 10, 25, 19, 52, 1, 40086, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imagenproducto',
            name='orden',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]