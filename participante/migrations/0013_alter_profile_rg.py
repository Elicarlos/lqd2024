# Generated by Django 3.2.20 on 2024-06-30 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participante', '0012_auto_20240622_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='RG',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
