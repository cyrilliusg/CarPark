# views.py
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Vehicle, Enterprise, Driver, VehicleDriverAssignment, Manager
from .serializers import VehicleSerializer, EnterpriseSerializer, DriverSerializer, VehicleDriverAssignmentSerializer


@method_decorator(csrf_protect, name='dispatch')
class ActiveVehicleDriverListAPIView(generics.ListAPIView):
    serializer_class = VehicleDriverAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()

        return VehicleDriverAssignment.objects.filter(
            is_active=True,
            vehicle__enterprise__in=enterprises
        )


@method_decorator(csrf_protect, name='dispatch')
class VehicleListAPIView(generics.ListAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()

        queryset = Vehicle.objects.filter(enterprise__in=enterprises)

        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            queryset = queryset.filter(vehicledriverassignment__is_active=True).prefetch_related(
                'vehicledriverassignment_set').distinct()
        return queryset


@method_decorator(csrf_protect, name='dispatch')
class EnterpriseListAPIView(generics.ListAPIView):
    # queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        return manager.enterprises.all()


@method_decorator(csrf_protect, name='dispatch')
class DriverListAPIView(generics.ListAPIView):
    # queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()
        return Driver.objects.filter(enterprise__in=enterprises)


@method_decorator(csrf_protect, name='dispatch')
class ActiveDriverAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vehicle_id):
        manager = get_object_or_404(Manager, user=request.user)
        enterprises = manager.enterprises.all()

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id, enterprise__in=enterprises)
            assignment = VehicleDriverAssignment.objects.filter(vehicle=vehicle, is_active=True).first()
            if assignment:
                serializer = DriverSerializer(assignment.driver)
                return Response(serializer.data)
            else:
                return Response({'detail': 'Активный водитель не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Vehicle.DoesNotExist:
            return Response({'detail': 'Автомобиль не найден или у вас нет доступа'}, status=status.HTTP_404_NOT_FOUND)
