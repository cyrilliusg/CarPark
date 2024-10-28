# serializers.py
from rest_framework import serializers
from .models import VehicleDriverAssignment, Vehicle, Driver, Enterprise


class VehicleSerializer(serializers.ModelSerializer):
    active_driver_id = serializers.SerializerMethodField()

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
        ]

    def get_active_driver_id(self, obj):
        assignment = VehicleDriverAssignment.objects.filter(vehicle=obj, is_active=True).first()
        if assignment:
            return assignment.driver.id
        return None


class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
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
