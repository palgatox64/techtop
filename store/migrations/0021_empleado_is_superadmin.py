from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_passwordresettoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='is_superadmin',
            field=models.BooleanField(default=False),
        ),
    ]