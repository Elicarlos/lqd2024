# Generated by Django 3.2.20 on 2024-06-18 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participante', '0006_rename_posto_de_trabalho_profile_posto_trabalho'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentofiscal',
            name='compradoREDE',
            field=models.BooleanField(default=False, verbose_name='Comprou na maquininha da PagBank?'),
        ),
    ]