# Generated by Django 5.1.1 on 2024-10-07 08:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0006_alter_vehicle_enterprise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='enterprise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='vehicle.enterprise', verbose_name='Предприятие'),
        ),
    ]
