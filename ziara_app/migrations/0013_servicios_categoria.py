# Generated by Django 5.1.1 on 2025-03-25 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziara_app', '0012_alter_servicios_precio'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicios',
            name='categoria',
            field=models.CharField(choices=[('B', 'Barba'), ('C', 'Cabello'), ('s', 'Spa')], default='', max_length=1),
        ),
    ]
