# Generated by Django 5.1.1 on 2024-12-27 08:19

import django.utils.timezone
import timezone_field.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0009_manager_nickname'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterprise',
            name='local_timezone',
            field=timezone_field.fields.TimeZoneField(default='UTC', verbose_name='Локальная таймзона'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='purchase_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата/время покупки (UTC)'),
        ),
    ]
