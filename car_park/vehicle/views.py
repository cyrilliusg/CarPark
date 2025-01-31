# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from .forms import EnterpriseForm, VehicleForm
from .models import Vehicle, Enterprise, Driver, VehicleDriverAssignment, Manager, VehicleGPSPoint, Route
from .pagination import CustomPageNumberPagination
from .serializers import VehicleSerializer, EnterpriseSerializer, DriverSerializer, VehicleDriverAssignmentSerializer, \
    VehicleGPSPointSerializer, VehicleGPSPointGeoSerializer, RouteSerializer

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.utils import timezone
import zoneinfo
from datetime import datetime


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


@login_required
def enterprise_edit_view(request, pk):
    enterprise = get_object_or_404(Enterprise, pk=pk)
    if request.method == 'POST':
        form = EnterpriseForm(request.POST, instance=enterprise)
        if form.is_valid():
            form.save()
            messages.success(request, "Таймзона предприятия обновлена.")
            return redirect('enterprise-list-view')
    else:
        form = EnterpriseForm(instance=enterprise)
    return render(request, 'enterprise_edit.html', {'form': form, 'enterprise': enterprise})


@login_required
def enterprise_vehicles_list_view(request, pk):
    # Проверяем, что предприятие доступно этому менеджеру
    manager = get_object_or_404(Manager, user=request.user)
    enterprise = get_object_or_404(Enterprise, pk=pk, managers=manager)

    vehicles = Vehicle.objects.filter(enterprise=enterprise)

    return render(request, 'enterprise_vehicles_list.html', {
        'enterprise': enterprise,
        'vehicles': vehicles,
    })


@login_required
def vehicle_add_view(request, pk):
    manager = get_object_or_404(Manager, user=request.user)
    enterprise = get_object_or_404(Enterprise, pk=pk, managers=manager)

    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.enterprise = enterprise
            vehicle.save()
            messages.success(request, "Машина добавлена успешно.")
            return redirect('enterprise-vehicles-list', pk=enterprise.id)
    else:
        form = VehicleForm()

    return render(request, 'vehicle_form.html', {
        'form': form,
        'enterprise': enterprise,
        'title': 'Добавление машины',
    })


@login_required
def vehicle_edit_view(request, pk, vehicle_id):
    manager = get_object_or_404(Manager, user=request.user)
    enterprise = get_object_or_404(Enterprise, pk=pk, managers=manager)

    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, enterprise=enterprise)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Машина обновлена.")
            return redirect('enterprise-vehicles-list', pk=enterprise.id)
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'vehicle_form.html', {
        'form': form,
        'enterprise': enterprise,
        'title': 'Редактирование машины',
    })


@login_required
def vehicle_delete_view(request, pk, vehicle_id):
    manager = get_object_or_404(Manager, user=request.user)
    enterprise = get_object_or_404(Enterprise, pk=pk, managers=manager)

    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, enterprise=enterprise)

    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, "Машина удалена.")
        return redirect('enterprise-vehicles-list', pk=enterprise.id)

    return render(request, 'vehicle_delete_confirm.html', {
        'vehicle': vehicle,
        'enterprise': enterprise
    })


@method_decorator(csrf_protect, name='dispatch')
class VehicleGPSPointListView(generics.ListAPIView):
    """
    GET /api/gps-points/?vehicle_id=...&start_time=...&end_time=...&format=geojson
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VehicleGPSPointSerializer  # Обычный JSON по умолчанию

    def get_queryset(self):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()

        queryset = VehicleGPSPoint.objects.all()

        # Получение vehicle_id из пути или параметров
        vehicle_id = self.kwargs.get('vehicle_id') or self.request.query_params.get('vehicle_id')
        if vehicle_id:
            # Проверяем принадлежность
            vehicle = get_object_or_404(Vehicle, pk=vehicle_id, enterprise__in=enterprises)
            queryset = queryset.filter(vehicle=vehicle)

        start_local_str = self.request.query_params.get('start_time')
        end_local_str = self.request.query_params.get('end_time')
        if start_local_str and end_local_str:
            fmt = "%Y-%m-%dT%H:%M"
            if vehicle_id:
                enterprise_tz = zoneinfo.ZoneInfo(vehicle.enterprise.local_timezone.key)
            else:
                enterprise_tz = zoneinfo.ZoneInfo("UTC")
            try:
                start_local = datetime.strptime(start_local_str, fmt)
                end_local = datetime.strptime(end_local_str, fmt)
            except ValueError as e:
                # Если формат не соответствует, можем вернуть пустой queryset или выбросить 400
                return queryset.none()

            start_local_aware = start_local.replace(tzinfo=enterprise_tz)
            end_local_aware = end_local.replace(tzinfo=enterprise_tz)
            start_utc = start_local_aware.astimezone(timezone.timezone.utc)
            end_utc = end_local_aware.astimezone(timezone.timezone.utc)

            queryset = queryset.filter(timestamp__range=(start_utc, end_utc))
        return queryset

    def list(self, request, *args, **kwargs):
        geojson_param = request.query_params.get('geojson', 'false')
        if geojson_param == 'true':
            self.serializer_class = VehicleGPSPointGeoSerializer
        return super().list(request, *args, **kwargs)


@method_decorator(csrf_protect, name='dispatch')
class VehiclePointsByRoutesView(APIView):
    """
    GET /api/routes/points/?vehicle_id=...&start_time=...&end_time=...
    start_time/end_time считаем локальными (таймзона предприятия). Переводим в UTC.
    Фильтруем маршруты, которые строго внутри [start_utc, end_utc].
    Собираем их точки.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()

        vehicle_id = request.query_params.get('vehicle_id')
        start_local_str = request.query_params.get('start_time')
        end_local_str = request.query_params.get('end_time')

        if not vehicle_id or not start_local_str or not end_local_str:
            return Response({"detail": "vehicle_id, start_time, end_time are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        vehicle = get_object_or_404(Vehicle, pk=vehicle_id, enterprise__in=enterprises)

        # Предположим, enterprise.local_timezone:
        # Но, не зная enterprise, можно взять 'Europe/Moscow' или UTC.
        # Допустим, берем "Europe/Moscow".
        enterprise_tz = zoneinfo.ZoneInfo(vehicle.enterprise.local_timezone.key)

        fmt = "%Y-%m-%dT%H:%M"
        try:
            start_local = datetime.strptime(start_local_str, fmt)
            end_local = datetime.strptime(end_local_str, fmt)
        except ValueError:
            return Response({"detail": "Invalid time format. Use YYYY-MM-DDTHH:MM"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Переводим naive -> aware
        start_local_aware = start_local.replace(tzinfo=enterprise_tz)
        end_local_aware = end_local.replace(tzinfo=enterprise_tz)

        # В UTC
        start_utc = start_local_aware.astimezone(timezone.timezone.utc)
        end_utc = end_local_aware.astimezone(timezone.timezone.utc)

        # Находим Routes.
        # Условие: route.start_time >= start_utc  AND route.end_time <= end_utc
        routes = Route.objects.filter(
            vehicle_id=vehicle_id,
            start_time__gte=start_utc,
            end_time__lte=end_utc
        )

        # теперь собираем точки, которые лежат внутри каждого route
        # вариант 1: общий список
        all_points = []
        for route in routes:
            points = VehicleGPSPoint.objects.filter(
                vehicle_id=vehicle_id,
                timestamp__gte=route.start_time,
                timestamp__lte=route.end_time
            )
            all_points.extend(points)

        if not all_points:
            return Response({"detail": "No Routes matches the given query."},
                            status=status.HTTP_200_OK)

        # сериализуем
        serializer = VehicleGPSPointSerializer(all_points, many=True, context={'exclude_fields': ['vehicle']})
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name='dispatch')
class RouteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        manager = get_object_or_404(Manager, user=self.request.user)
        enterprises = manager.enterprises.all()

        vehicle_id = request.query_params.get('vehicle_id')
        start_local_str = request.query_params.get('start_time')
        end_local_str = request.query_params.get('end_time')

        if not vehicle_id or not start_local_str or not end_local_str:
            return Response({"detail": "vehicle_id, start_time, end_time are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        vehicle = get_object_or_404(Vehicle, pk=vehicle_id, enterprise__in=enterprises)

        # 2) Локальная таймзона
        enterprise_tz = zoneinfo.ZoneInfo(vehicle.enterprise.local_timezone.key)

        fmt = "%Y-%m-%dT%H:%M"
        try:
            start_local = datetime.strptime(start_local_str, fmt)
            end_local = datetime.strptime(end_local_str, fmt)
        except ValueError:
            return Response({"detail": "Invalid time format. Use YYYY-MM-DDTHH:MM"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Переводим naive -> aware
        start_local_aware = start_local.replace(tzinfo=enterprise_tz)
        end_local_aware = end_local.replace(tzinfo=enterprise_tz)

        # В UTC
        start_utc = start_local_aware.astimezone(timezone.timezone.utc)
        end_utc = end_local_aware.astimezone(timezone.timezone.utc)

        # 3) Фильтруем маршруты, которые ЦЕЛИКОМ внутри [start_utc, end_utc]
        #    route.start_time >= start_utc AND route.end_time <= end_utc
        routes = Route.objects.filter(
            vehicle_id=vehicle_id,
            start_time__gte=start_utc,
            end_time__lte=end_utc
        )

        # 4) Сериализация
        # Передаём context={'request': ..., 'ors_api_key': '...'}
        # Это нужно для reverse geocode
        serializer = RouteSerializer(
            routes,
            many=True,
            context={
                'request': request,
                'ors_api_key': "5b3ce3597851110001cf62489efd2bfc610f4a348f0719877a5d6a56"
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
