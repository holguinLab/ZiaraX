# Generated by Django 4.2.11 on 2025-04-07 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ziara_app', '0034_alter_productos_categoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='email',
            field=models.EmailField(max_length=100, unique=True),
        ),
    ]
