# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Vehicle, Enterprise, Driver, VehicleDriverAssignment
from .serializers import VehicleSerializer, EnterpriseSerializer, DriverSerializer, VehicleDriverAssignmentSerializer


class ActiveVehicleDriverListAPIView(generics.ListAPIView):
    queryset = VehicleDriverAssignment.objects.filter(is_active=True)
    serializer_class = VehicleDriverAssignmentSerializer


class VehicleListAPIView(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        queryset = Vehicle.objects.all()

        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            queryset = Vehicle.objects.filter(vehicledriverassignment__is_active=True).prefetch_related(
                'vehicledriverassignment_set').distinct()
        return queryset


class EnterpriseListAPIView(generics.ListAPIView):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer


class DriverListAPIView(generics.ListAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class ActiveDriverAPIView(APIView):
    def get(self, request, vehicle_id):
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            assignment = VehicleDriverAssignment.objects.filter(vehicle=vehicle, is_active=True).first()
            if assignment:
                serializer = DriverSerializer(assignment.driver)
                return Response(serializer.data)
            else:
                return Response({'detail': 'Активный водитель не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Vehicle.DoesNotExist:
            return Response({'detail': 'Автомобиль не найден'}, status=status.HTTP_404_NOT_FOUND)
