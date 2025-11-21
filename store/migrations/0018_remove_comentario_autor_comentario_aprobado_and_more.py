import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_comentario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comentario',
            name='autor',
        ),
        migrations.AddField(
            model_name='comentario',
            name='aprobado',
            field=models.BooleanField(default=False, help_text='Marcar si el comentario es público'),
        ),
        migrations.AddField(
            model_name='comentario',
            name='cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.cliente'),
        ),
    ]