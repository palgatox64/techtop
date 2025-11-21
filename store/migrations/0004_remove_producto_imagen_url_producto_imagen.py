from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_cliente_telefono'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='imagen_url',
        ),
        migrations.AddField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='productos/'),
        ),
    ]