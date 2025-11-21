from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_remove_producto_imagen_url_producto_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='tipo_usuario',
            field=models.CharField(choices=[('cliente', 'Cliente'), ('admin', 'Administrador')], default='cliente', max_length=10),
        ),
    ]