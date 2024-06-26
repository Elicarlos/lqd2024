# Generated by Django 3.2.20 on 2024-06-16 23:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lojista', '0004_adesaolojista_atendido_por'),
    ]

    operations = [
        migrations.CreateModel(
            name='Localizacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=250)),
                ('descricao', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='lojista',
            name='Localizacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lojista.localizacao'),
        ),
    ]
