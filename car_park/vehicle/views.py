# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .models import Vehicle, Enterprise, Driver, VehicleDriverAssignment, Manager
from .pagination import CustomPageNumberPagination
from .serializers import VehicleSerializer, EnterpriseSerializer, DriverSerializer, VehicleDriverAssignmentSerializer

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


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
class VehicleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination  # Указываем кастомный пагинатор

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()

        queryset = Vehicle.objects.filter(enterprise__in=enterprises)

        # Фильтр активных транспортных средств
        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            queryset = queryset.filter(vehicledriverassignment__is_active=True).distinct()
        return queryset

    def perform_create(self, serializer):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprise = serializer.validated_data.get('enterprise')
        if enterprise in manager.enterprises.all():
            serializer.save()
        else:
            raise PermissionDenied("Вы не можете создавать транспортные средства для этого предприятия.")


@method_decorator(csrf_protect, name='dispatch')
class VehicleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        vehicle = get_object_or_404(Vehicle, pk=self.kwargs['pk'], enterprise__in=manager.enterprises.all())
        return vehicle

    def perform_update(self, serializer):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprise = serializer.validated_data.get('enterprise', serializer.instance.enterprise)
        if enterprise in manager.enterprises.all():
            serializer.save()
        else:
            raise PermissionDenied("Вы не можете обновлять транспортные средства этого предприятия.")

    def perform_destroy(self, instance):
        manager = get_object_or_404(Manager, user=self.request.user)
        if instance.enterprise in manager.enterprises.all():
            instance.delete()
        else:
            raise PermissionDenied("Вы не можете удалять транспортные средства этого предприятия.")


@method_decorator(csrf_protect, name='dispatch')
class EnterpriseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EnterpriseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        return manager.enterprises.all()

    def perform_create(self, serializer):
        # Если вы хотите ограничить создание предприятий только менеджерами
        serializer.save()
        # Если требуется добавить созданное предприятие к списку предприятий менеджера
        manager = get_object_or_404(Manager, user=self.request.user)
        manager.enterprises.add(serializer.instance)


@method_decorator(csrf_protect, name='dispatch')
class EnterpriseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnterpriseSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprise = get_object_or_404(Enterprise, pk=self.kwargs['pk'], managers=manager)
        return enterprise

    def perform_update(self, serializer):
        # Проверка прав доступа не требуется, так как get_object уже фильтрует доступные предприятия
        serializer.save()

    def perform_destroy(self, instance):
        manager = get_object_or_404(Manager, user=self.request.user)
        if instance in manager.enterprises.all():
            instance.delete()
        else:
            raise PermissionDenied("Вы не можете удалять это предприятие.")


@method_decorator(csrf_protect, name='dispatch')
class DriverListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()
        return Driver.objects.filter(enterprise__in=enterprises)

    def perform_create(self, serializer):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprise = serializer.validated_data.get('enterprise')
        if enterprise in manager.enterprises.all():
            serializer.save()
        else:
            raise PermissionDenied("Вы не можете создавать водителей для этого предприятия.")


@method_decorator(csrf_protect, name='dispatch')
class DriverRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        driver = get_object_or_404(Driver, pk=self.kwargs['pk'], enterprise__in=manager.enterprises.all())
        return driver

    def perform_update(self, serializer):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprise = serializer.validated_data.get('enterprise', serializer.instance.enterprise)
        if enterprise in manager.enterprises.all():
            serializer.save()
        else:
            raise PermissionDenied("Вы не можете обновлять водителей этого предприятия.")

    def perform_destroy(self, instance):
        manager = get_object_or_404(Manager, user=self.request.user)
        if instance.enterprise in manager.enterprises.all():
            instance.delete()
        else:
            raise PermissionDenied("Вы не можете удалять водителей этого предприятия.")


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


@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON.'}, status=status.HTTP_400_BAD_REQUEST)

        if not username or not password:
            return JsonResponse({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'detail': 'Login successful.'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return JsonResponse({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('enterprise-list-view')
        else:
            return render(request, 'login.html', {'error': 'Неверные учетные данные'})
    return render(request, 'login.html')

@login_required
def enterprise_list_view(request):
    manager = get_object_or_404(Manager, user=request.user)
    enterprises = manager.enterprises.all()
    return render(request, 'enterprise_list.html', {'enterprises': enterprises})