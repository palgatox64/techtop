import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_producto_descuento'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=100, unique=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usado', models.BooleanField(default=False)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reset_tokens', to='store.cliente')),
            ],
            options={
                'db_table': 'PASSWORD_RESET_TOKENS',
            },
        ),
    ]