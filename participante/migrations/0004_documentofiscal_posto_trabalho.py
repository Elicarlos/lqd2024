# Generated by Django 3.2.20 on 2024-06-17 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('participante', '0003_auto_20240616_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentofiscal',
            name='posto_trabalho',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='participante.postotrabalho', verbose_name='Posto de Trabalho'),
        ),
    ]
