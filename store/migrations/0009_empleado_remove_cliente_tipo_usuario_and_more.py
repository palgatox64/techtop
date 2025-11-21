import store.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_imagenproducto_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id_empleado', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, validators=[store.validators.validate_name])),
                ('apellidos', models.CharField(max_length=150, validators=[store.validators.validate_name])),
                ('email', models.EmailField(max_length=100, unique=True, validators=[store.validators.validate_email_extended])),
                ('pass_hash', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=9, validators=[store.validators.validate_chilean_phone])),
                ('cargo', models.CharField(default='Empleado', max_length=100)),
                ('fecha_contratacion', models.DateField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Empleado',
                'verbose_name_plural': 'Empleados',
                'db_table': 'EMPLEADOS',
            },
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='tipo_usuario',
        ),
        migrations.AlterModelTable(
            name='cliente',
            table='CLIENTES',
        ),
    ]