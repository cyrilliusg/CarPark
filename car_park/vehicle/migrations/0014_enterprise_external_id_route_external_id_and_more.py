# Generated by Django 5.1.1 on 2025-02-13 12:39

import uuid
from django.db import migrations, models

def generate_uuids(apps, schema_editor):
    Enterprise = apps.get_model('vehicle', 'Enterprise')
    Route = apps.get_model('vehicle', 'Route')
    Vehicle = apps.get_model('vehicle', 'Vehicle')

    for obj in Enterprise.objects.all():
        obj.external_id = uuid.uuid4()
        obj.save()

    for obj in Route.objects.all():
        obj.external_id = uuid.uuid4()
        obj.save()

    for obj in Vehicle.objects.all():
        obj.external_id = uuid.uuid4()
        obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0013_route_end_location_route_start_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterprise',
            name='external_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name='route',
            name='external_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='external_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),

        migrations.RunPython(generate_uuids),  # Генерация UUID
    ]
