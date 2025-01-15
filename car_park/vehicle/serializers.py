# serializers.py
from rest_framework import serializers
from .models import VehicleDriverAssignment, Vehicle, Driver, Enterprise, VehicleGPSPoint


class VehicleSerializer(serializers.ModelSerializer):
    active_driver_id = serializers.SerializerMethodField()
    id = serializers.IntegerField(read_only=True)
    purchase_datetime_local = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'vin',
            'price',
            'release_year',
            'mileage',
            'color',
            'transmission_type',
            'configuration',
            'enterprise',
            'drivers',
            'active_driver_id',  # Добавили поле здесь
            'purchase_datetime',  # Хранимая в UTC
            'purchase_datetime_local',  # Конвертированная в tz предприятия
        ]

    def get_active_driver_id(self, obj):
        assignment = VehicleDriverAssignment.objects.filter(vehicle=obj, is_active=True).first()
        if assignment:
            return assignment.driver.id
        return None

    def get_purchase_datetime_local(self, obj):
        # берем tzinfo из enterprise
        enterprise_tz = obj.enterprise.local_timezone  # TimeZoneField => объект tzinfo
        if not obj.purchase_datetime:
            return None
        # Переводим из UTC в локальную таймзону
        # Django datetime поля обычно offset-aware (UTC).
        return obj.purchase_datetime.astimezone(enterprise_tz).isoformat()


class EnterpriseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Enterprise
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'name', 'salary', 'enterprise', 'vehicles']

    def get_vehicles(self, obj):
        assignments = VehicleDriverAssignment.objects.filter(driver=obj)
        return VehicleDriverAssignmentSerializer(assignments, many=True).data


class VehicleDriverAssignmentSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    driver = DriverSerializer()

    class Meta:
        model = VehicleDriverAssignment
        fields = ['id', 'vehicle', 'driver', 'is_active']


class VehicleGPSPointSerializer(serializers.ModelSerializer):
    # Координаты как список [lng, lat] или [lat, lng] - на ваше усмотрение
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = VehicleGPSPoint
        fields = ['id', 'vehicle', 'timestamp', 'coordinates']

    def get_coordinates(self, obj):
        # obj.location — Point (x=долгота, y=широта)
        # или наоборот, в зависимости от используемой SRID
        if obj.location:
            return [obj.location.x, obj.location.y]
        return None

class VehicleGPSPointGeoSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default='Feature')
    geometry = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()

    class Meta:
        model = VehicleGPSPoint
        fields = ['type', 'geometry', 'properties']

    def get_geometry(self, obj):
        if obj.location:
            return {
                "type": "Point",
                "coordinates": [obj.location.x, obj.location.y]
            }
        return None

    def get_properties(self, obj):
        return {
            "id": obj.id,
            "vehicle": obj.vehicle_id,
            "timestamp": obj.timestamp.isoformat()
        }
