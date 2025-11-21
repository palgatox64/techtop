from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_pedido_metodo_pago_notificacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]