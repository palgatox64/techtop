from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_imagenproducto_orden'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imagenproducto',
            options={},
        ),
        migrations.RemoveField(
            model_name='imagenproducto',
            name='descripcion',
        ),
        migrations.RemoveField(
            model_name='imagenproducto',
            name='fecha_subida',
        ),
        migrations.RemoveField(
            model_name='imagenproducto',
            name='orden',
        ),
    ]