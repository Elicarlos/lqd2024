# Generated by Django 3.2.20 on 2024-06-17 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lojista', '0005_auto_20240616_2053'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lojista',
            old_name='Localizacao',
            new_name='localizacao',
        ),
    ]
