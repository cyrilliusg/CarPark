# Generated by Django 5.1.1 on 2024-10-07 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0005_enterprise_driver_vehicle_enterprise_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='enterprise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='vehicle.enterprise', verbose_name='Предприятие'),
        ),
    ]
