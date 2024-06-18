# Generated by Django 3.2.20 on 2024-06-18 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('participante', '0004_documentofiscal_posto_trabalho'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='posto_de_trabalho',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='participante.postotrabalho', verbose_name='Posto de trabalho'),
        ),
    ]