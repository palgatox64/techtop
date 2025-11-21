from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_empleado_remove_cliente_tipo_usuario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]