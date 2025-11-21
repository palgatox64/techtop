import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_imagenproducto_options_cliente_rut_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransaccionWebpay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(help_text='Token generado por Transbank', max_length=255, unique=True)),
                ('buy_order', models.CharField(help_text='Orden de compra única', max_length=100, unique=True)),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('AUTORIZADO', 'Autorizado'), ('RECHAZADO', 'Rechazado'), ('ANULADO', 'Anulado')], default='PENDIENTE', max_length=20)),
                ('response_code', models.CharField(blank=True, help_text='Código de respuesta', max_length=10, null=True)),
                ('authorization_code', models.CharField(blank=True, help_text='Código de autorización', max_length=10, null=True)),
                ('payment_type_code', models.CharField(blank=True, help_text='Tipo de pago', max_length=10, null=True)),
                ('card_number', models.CharField(blank=True, help_text='Últimos 4 dígitos de la tarjeta', max_length=20, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones_webpay', to='store.pedido')),
            ],
            options={
                'verbose_name': 'Transacción Webpay',
                'verbose_name_plural': 'Transacciones Webpay',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]