# Generated by Django 3.2.20 on 2024-06-13 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lojista', '0002_adesaolojista'),
    ]

    operations = [
        migrations.AddField(
            model_name='adesaolojista',
            name='atendido',
            field=models.BooleanField(default=False),
        ),
    ]
