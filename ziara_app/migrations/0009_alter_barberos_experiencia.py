# Generated by Django 5.1.1 on 2025-03-20 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziara_app', '0008_barberos_experiencia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barberos',
            name='experiencia',
            field=models.IntegerField(blank=True, default='', null=True),
        ),
    ]
