# Generated by Django 5.1.1 on 2025-03-27 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziara_app', '0018_alter_citas_estado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citas',
            name='servicio',
        ),
        migrations.AlterField(
            model_name='servicios',
            name='precio',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]
