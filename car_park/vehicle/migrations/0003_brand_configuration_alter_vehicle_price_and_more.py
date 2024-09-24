# Generated by Django 5.1.1 on 2024-09-24 20:41

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0002_vehicle_vin_alter_vehicle_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название бренда')),
                ('country', models.CharField(max_length=100, verbose_name='Страна')),
            ],
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название комплектации')),
                ('tank_capacity', models.DecimalField(decimal_places=1, max_digits=5, verbose_name='Объем бака (л)')),
                ('payload', models.PositiveIntegerField(verbose_name='Грузоподъемность (кг)')),
                ('seats_number', models.PositiveIntegerField(verbose_name='Количество мест')),
            ],
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Стоимость'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='configuration',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='vehicle.configuration', verbose_name='Комплектация'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название модели')),
                ('vehicle_type', models.CharField(choices=[('Passenger', 'Легковой'), ('Truck', 'Грузовой'), ('Bus', 'Автобус'), ('SUV', 'Внедорожник'), ('Van', 'Фургон')], max_length=50, verbose_name='Тип транспортного средства')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='vehicle.brand', verbose_name='Бренд')),
            ],
        ),
        migrations.AddField(
            model_name='configuration',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='configurations', to='vehicle.model', verbose_name='Модель'),
        ),
    ]
