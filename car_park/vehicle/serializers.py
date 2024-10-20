# serializers.py
from rest_framework import serializers
from .models import VehicleDriverAssignment, Vehicle, Driver, Enterprise


class VehicleSerializer(serializers.ModelSerializer):
    active_driver = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = '__all__'

    def get_active_driver(self, obj):
        assignment = VehicleDriverAssignment.objects.filter(vehicle=obj, is_active=True).first()
        if assignment:
            return DriverSerializer(assignment.driver).data
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
