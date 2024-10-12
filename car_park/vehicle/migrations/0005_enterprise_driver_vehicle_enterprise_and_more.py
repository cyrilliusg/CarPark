# Generated by Django 5.1.1 on 2024-10-07 08:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0004_alter_configuration_tank_capacity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название предприятия')),
                ('city', models.CharField(max_length=100, verbose_name='Город')),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя водителя')),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Зарплата')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drivers', to='vehicle.enterprise', verbose_name='Предприятие')),
            ],
        ),
        migrations.AddField(
            model_name='vehicle',
            name='enterprise',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='vehicle.enterprise', verbose_name='Предприятие'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='VehicleDriverAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False, verbose_name='Активный водитель')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.driver', verbose_name='Водитель')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.vehicle', verbose_name='Автомобиль')),
            ],
            options={
                'unique_together': {('vehicle', 'driver')},
            },
        ),
        migrations.AddField(
            model_name='vehicle',
            name='drivers',
            field=models.ManyToManyField(related_name='vehicles', through='vehicle.VehicleDriverAssignment', to='vehicle.driver', verbose_name='Водители'),
        ),
    ]
