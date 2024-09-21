# Generated by Django 5.1.1 on 2024-09-21 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='vin',
            field=models.CharField(default=1, max_length=17, unique=True, verbose_name='VIN'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='transmission_type',
            field=models.CharField(choices=[('Механическая', 'Механические'), ('Автоматическая', 'Автоматические'), ('Бесступенчатая', 'Бесступенчатые'), ('Роботизированная', 'Роботизированные'), ('Последовательная механическая и полуавтоматическая', 'Последовательные механические и полуавтоматические')], default='Механическая', max_length=50, verbose_name='Тип трансмиссии'),
        ),
    ]