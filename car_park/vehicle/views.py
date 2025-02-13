# views.py
import csv
import io
import zipfile

import folium
from django.contrib.gis.geos import Point
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
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
from .modules.ors import reverse_geocode_ors, KEY
from .pagination import CustomPageNumberPagination
from .serializers import VehicleSerializer, EnterpriseSerializer, DriverSerializer, VehicleDriverAssignmentSerializer, \
    VehicleGPSPointSerializer, VehicleGPSPointGeoSerializer, RouteSerializer

from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.utils import timezone
import zoneinfo
from datetime import datetime
from datetime import time


import uuid


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


@login_required
def vehicle_detail_view(request, pk, vehicle_id):
    # 1) Проверить, что enterprise принадлежит менеджеру
    manager = get_object_or_404(Manager, user=request.user)
    enterprise = get_object_or_404(Enterprise, pk=pk, managers=manager)

    # 2) Получить машину
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, enterprise=enterprise)

    # 3) Фильтр дат (локальная таймзона)
    start_str = request.GET.get('start_date')
    end_str = request.GET.get('end_date')
    routes = []

    local_tz = zoneinfo.ZoneInfo(vehicle.enterprise.local_timezone.key)

    if start_str and end_str:
        # Предположим формат YYYY-MM-DD
        try:
            fmt = "%m/%d/%Y %I:%M %p"
            start_date = datetime.strptime(start_str, fmt).date()
            end_date = datetime.strptime(end_str, fmt).date()

            # в локальную TZ
            # Устанавливаем границы дня
            start_local = datetime.combine(start_date, time.min, tzinfo=local_tz)
            end_local = datetime.combine(end_date, time.max, tzinfo=local_tz)
            # переводим в UTC
            start_utc = start_local.astimezone(timezone.timezone.utc)
            end_utc = end_local.astimezone(timezone.timezone.utc)
            # Фильтруем поездки, которые целиком в [start_utc, end_utc]
            routes = Route.objects.filter(
                vehicle=vehicle,
                start_time__gte=start_utc,
                end_time__lte=end_utc
            ).order_by('start_time')

            # Обогащаем данные адресами через API
            for route in routes:
                if route.start_location:
                    route.start_address = reverse_geocode_ors(
                        KEY, route.start_location.y, route.start_location.x
                    )
                if route.end_location:
                    route.end_address = reverse_geocode_ors(
                        KEY, route.end_location.y, route.end_location.x
                    )


        except ValueError:
            # Ошибка формата дат
            pass

    # Рендер
    context = {
        'enterprise': enterprise,
        'vehicle': vehicle,
        'routes': routes,
        'start_date': start_str,
        'end_date': end_str,
    }
    return render(request, 'vehicle_detail.html', context)


@login_required
def vehicle_map_view(request, pk, vehicle_id):
    manager = get_object_or_404(Manager, user=request.user)
    enterprise = get_object_or_404(Enterprise, pk=pk, managers=manager)
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, enterprise=enterprise)

    route_id = request.GET.get('route_id')
    if not route_id:
        return HttpResponse("Не указан route_id")

    route = get_object_or_404(Route, pk=route_id, vehicle=vehicle)
    # Получаем точки для этого Route (между route.start_time и route.end_time)
    points = VehicleGPSPoint.objects.filter(
        vehicle=vehicle,
        timestamp__gte=route.start_time,
        timestamp__lte=route.end_time
    ).order_by('timestamp')

    # Если нет точек, просто сообщаем
    if not points.exists():
        return HttpResponse("Нет точек для выбранной поездки")

    # 1) Найдём среднюю точку для центра карты
    avg_lat = sum(p.location.y for p in points) / len(points)
    avg_lon = sum(p.location.x for p in points) / len(points)

    # 2) Создадим Folium map
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=8, width='600px', height='380px')

    # 3) Соберём координаты в формате [[lat, lon], [lat, lon], ...]
    coords = [[p.location.y, p.location.x] for p in points]

    # 4) Добавим линию
    folium.PolyLine(coords, color='blue', weight=4, opacity=0.7).add_to(m)

    # 5) Добавим маркеры начала/конца
    first = coords[0]
    last = coords[-1]
    folium.Marker(first, tooltip="Начало маршрута").add_to(m)
    folium.Marker(last, tooltip="Конец маршрута").add_to(m)

    # 6) Получаем HTML
    map_html = m._repr_html_()  # Folium генерирует iframe HTML

    # Если запрос AJAX (например, из fetch), возвращаем только фрагмент
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_fragment = render_to_string('partials/vehicle_map.html', {
            'map_html': map_html,
            'route': route
        })
        return HttpResponse(html_fragment)
    else:
        # Либо оставляем вариант для прямого перехода на страницу
        return render(request, 'vehicle_map.html', {'map_html': map_html, 'route': route})

    # return render(request, 'vehicle_map.html', {'map_html': map_html, 'route': route})



@method_decorator(csrf_protect, name='dispatch')
class ExportEnterpriseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        В локальной TZ предприятия.
        """
        enterprise_id = request.query_params.get('enterprise_id')
        start_str = request.query_params.get('start_time')
        end_str = request.query_params.get('end_time')
        out_format = request.query_params.get('format', 'json')

        # 1) Проверка доступа
        manager = get_object_or_404(Manager, user=request.user)
        enterprise = get_object_or_404(Enterprise, pk=enterprise_id, managers=manager)

        # 2) Локальная таймзона
        local_tz = zoneinfo.ZoneInfo(enterprise.local_timezone.key)

        # 3) Конверсия дат
        # Допустим формат "YYYY-MM-DDTHH:MM"
        enterprise_tz = zoneinfo.ZoneInfo(enterprise.local_timezone.key)

        fmt = "%Y-%m-%dT%H:%M"
        try:
            start_local = datetime.strptime(start_str, fmt)
            end_local = datetime.strptime(end_str, fmt)
        except ValueError:
            return Response({"detail": "Invalid time format. Use YYYY-MM-DDTHH:MM"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Переводим naive -> aware
        start_local_aware = start_local.replace(tzinfo=enterprise_tz)
        end_local_aware = end_local.replace(tzinfo=enterprise_tz)

        # В UTC
        start_utc = start_local_aware.astimezone(timezone.timezone.utc)
        end_utc = end_local_aware.astimezone(timezone.timezone.utc)

        # 4) Собираем данные:
        #   a) enterprise info
        #   b) vehicles of this enterprise
        vehicles = Vehicle.objects.filter(enterprise=enterprise)
        #   c) routes (поездки) за диапазон, для каждой машины
        routes_data = {}

        for v in vehicles:
            v_routes = list(Route.objects.filter(
                vehicle=v,
                start_time__gte=start_utc,
                end_time__lte=end_utc
            ))  # Преобразуем QuerySet в список сразу
            routes_data[v.id] = v_routes  # Храним маршруты в словаре

        # 5) Формируем структуру Python (для JSON) или CSV
        if out_format == 'json':
            return _export_json(enterprise, vehicles, routes_data)
        elif out_format == 'csv':
            return _export_csv(enterprise, vehicles, routes_data)
        else:
            return Response({"detail": "Unsupported format"}, status=status.HTTP_400_BAD_REQUEST)


def _export_json(enterprise: Enterprise,
                 vehicles: list[Vehicle],
                 routes_data: dict[str, list[Route]]):
    """
    Пример JSON структуры:
    {
      "enterprise": {
         "external_id": ...,
         "name": ...,
         "city": ...
      },
      "vehicles": [
        {
          "external_id": ...,
          "vin": ...,
          "price": ...,
          "release_year": ...,
          "mileage": ...,
          ...
          "routes": [
            {
              "external_id": ...,
              "start_time": ...,
              "end_time": ...,
              "gps_points": [ {timestamp, lat, lon}, ... ]
            },
            ...
          ]
        },
        ...
      ]
    }
    """
    data = {
        "enterprise": {
            "external_id": str(enterprise.external_id),
            "name": enterprise.name,
            "city": enterprise.city,
            "local_timezone": str(enterprise.local_timezone),
        },
        "vehicles": []
    }
    for item in vehicles:
        vehicle_dict = {
            "external_id": str(item.external_id),
            "vin": item.vin,
            "price": str(item.price),
            "release_year": item.release_year,
            "mileage": item.mileage,
            "routes": []
        }

        # Достаём маршруты по ID без `next()`
        route_info = routes_data.get(item.id, [])

        for r in route_info:
            gps_points_qs = VehicleGPSPoint.objects.filter(
                vehicle=item,
                timestamp__gte=r.start_time,
                timestamp__lte=r.end_time
            ).order_by('timestamp')

            gps_points = [
                {"timestamp": gp.timestamp.isoformat(), "location": [gp.location.x, gp.location.y]}
                for gp in gps_points_qs
            ]

            vehicle_dict["routes"].append({
                "external_id": str(r.external_id),
                "start_time": r.start_time.isoformat(),
                "end_time": r.end_time.isoformat(),
                "duration": str(r.duration),
                "gps_points": gps_points,
            })

        data["vehicles"].append(vehicle_dict)

    response = Response(data)
    response["Content-Disposition"] = 'attachment; filename="export.json"'

    return response


def _export_csv(enterprise: Enterprise,
                vehicles: list[Vehicle],
                routes_data: dict[str, list[Route]]):
    """
    Пример CSV: несколько CSV файлов в одном zip —
    (1) enterprise.csv, (2) vehicles.csv, (3) routes.csv, (4) gps_points.csv.
    Или всё в одном — на ваше усмотрение.

    Здесь пример 'многий CSV -> один HttpResponse' c zip.
    """
    import csv
    import io
    import zipfile

    # Создадим BytesIO для ZIP
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:

        # 1) enterprise.csv
        csvfile = io.StringIO()
        writer = csv.writer(csvfile)
        writer.writerow(["external_id", "name", "city", "local_timezone"])
        writer.writerow([str(enterprise.external_id), enterprise.name, enterprise.city, enterprise.local_timezone])
        zf.writestr("enterprise.csv", csvfile.getvalue())

        # 2) vehicles.csv
        csvfile = io.StringIO()
        writer = csv.writer(csvfile)
        writer.writerow(["vehicle_external_id", "vin", "price", "release_year", "mileage"])

        # 3) routes.csv
        csvfile_routes = io.StringIO()
        writer_routes = csv.writer(csvfile_routes)
        writer_routes.writerow(["route_external_id", "vehicle_external_id", "start_time", "end_time", "duration"])

        # 4) gps_points.csv
        csvfile_gps_points = io.StringIO()
        writer_gps_points = csv.writer(csvfile_gps_points)
        writer_gps_points.writerow(["route_external_id", "timestamp", "lon", "lat"])

        for vehicle in vehicles:
            # 2) vehicles.csv
            writer.writerow([str(vehicle.external_id), vehicle.vin, str(vehicle.price), vehicle.release_year, vehicle.mileage])

            # 3) routes.csv
            route_info = routes_data.get(vehicle.id, [])
            for r in route_info:
                writer_routes.writerow(
                    [str(r.external_id), str(vehicle.external_id), r.start_time.isoformat(), r.end_time.isoformat(),
                     str(r.duration)])

                # 4) gps_points.csv
                gps_points_qs = VehicleGPSPoint.objects.filter(
                    vehicle=vehicle,
                    timestamp__gte=r.start_time,
                    timestamp__lte=r.end_time
                ).order_by('timestamp')
                for gp in gps_points_qs:
                    writer_gps_points.writerow([
                        str(r.external_id),
                        gp.timestamp.isoformat(),
                        gp.location.x,
                        gp.location.y
                    ])

        # 2) vehicles.csv
        zf.writestr("vehicles.csv", csvfile.getvalue())
        # 3) routes.csv
        zf.writestr("routes.csv", csvfile_routes.getvalue())
        # 4) gps_points.csv
        zf.writestr("gps_points.csv", csvfile_gps_points.getvalue())

    # Вернём zip
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="enterprise_export.zip"'
    return response


@method_decorator(csrf_protect, name='dispatch')
class ImportEnterpriseDataJSONView(APIView):
    """
    POST /api/import-enterprise-data-json/
    JSON-структура (как при экспорте).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        manager = get_object_or_404(Manager, user=request.user)

        try:
            data = request.data  # уже dict (DRF автоматически JSON->dict)
        except Exception as e:
            return Response({"detail": f"Invalid JSON: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        # print(data)

        enterprise_data = data.get("enterprise")
        if not enterprise_data:
            return Response({"detail": "No 'enterprise' key found in JSON"}, status=400)

        # 1) Импорт/обновление Enterprise
        enterprise_extid = enterprise_data.get("external_id")
        if not enterprise_extid:
            return Response({"detail": "Missing enterprise.external_id"}, status=400)
        enterprise_obj, _ = Enterprise.objects.update_or_create(
            external_id=enterprise_extid,
            defaults={
                "name": enterprise_data.get("name", "NoName"),
                "city": enterprise_data.get("city", "NoCity"),
                "local_timezone": enterprise_data.get("local_timezone", "UTC"),
            }
        )
        # привязываем к менеджеру, если нужно
        manager.enterprises.add(enterprise_obj)


        # 2) Импорт vehicles
        vehicles_list = data.get("vehicles", [])
        for vdict in vehicles_list:
            vextid = vdict.get("external_id")
            if not vextid:
                continue  # Или выдать ошибку

            vehicle_obj, _ = Vehicle.objects.update_or_create(
                external_id=vextid,
                defaults={
                    "vin": vdict.get("vin", ""),
                    "price": vdict.get("price", "0"),
                    "release_year": vdict.get("release_year", 2000),
                    "mileage": vdict.get("mileage", 0),
                    "enterprise": enterprise_obj,
                    # color, configuration, etc. можно добавить
                }
            )
            # 3) Импорт routes
            routes = vdict.get("routes", [])
            for rdict in routes:
                rextid = rdict.get("external_id")
                if not rextid:
                    continue

                start_time = parse_datetime(rdict.get("start_time"))
                end_time = parse_datetime(rdict.get("end_time"))

                route_obj, _ = Route.objects.update_or_create(
                    external_id=rextid,
                    defaults={
                        "vehicle": vehicle_obj,
                        "start_time": start_time,
                        "end_time": end_time
                    }
                )
                # 4) Импорт gps_points
                gps_points = rdict.get("gps_points", [])
                for gpd in gps_points:
                    ts = gpd.get("timestamp")
                    coords = gpd.get("location")  # [lon, lat]
                    if not coords:
                        continue
                    VehicleGPSPoint.objects.create(
                        vehicle=vehicle_obj,
                        timestamp=ts,
                        location=Point(coords[0], coords[1], srid=4326)
                    )

        return Response({"detail": "Import (JSON) successful"}, status=200)


@method_decorator(csrf_protect, name='dispatch')
class ImportEnterpriseDataCSVView(APIView):
    """
    POST /api/import-enterprise-data-csv/
    Принимает multipart/form-data
    - file: zip-архив с enterprise.csv, vehicles.csv, routes.csv, gps_points.csv
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        manager = get_object_or_404(Manager, user=request.user)

        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "No file uploaded (expecting zip)."}, status=400)

        # Открываем как zip
        try:
            with zipfile.ZipFile(file, 'r') as zf:
                # Ищем внутри 'enterprise.csv', 'vehicles.csv', etc.
                enterprise_csv = zf.read('enterprise.csv').decode('utf-8')
                vehicles_csv = zf.read('vehicles.csv').decode('utf-8')
                routes_csv = zf.read('routes.csv').decode('utf-8')
                gps_csv = zf.read('gps_points.csv').decode('utf-8')
        except Exception as e:
            return Response({"detail": f"Error reading zip: {e}"}, status=400)

        # 1) Парсим enterprise.csv
        #    Пример: id, name, city, local_timezone
        enterprise_reader = csv.reader(io.StringIO(enterprise_csv))
        header = next(enterprise_reader)  # ['external_id','name','city','local_timezone']
        enterprise_data = next(enterprise_reader, None)
        if not enterprise_data:
            return Response({"detail":"No enterprise data in csv"}, status=400)
        ent_external_id, ent_name, ent_city, ent_tz = enterprise_data

        enterprise_obj, _ = Enterprise.objects.update_or_create(
            external_id=ent_external_id,
            defaults={
                'name': ent_name,
                'city': ent_city,
                'local_timezone': ent_tz
            }
        )
        manager.enterprises.add(enterprise_obj)

        # 2) vehicles.csv
        #    vehicle_external_id, vin, price, release_year, mileage
        vehicle_reader = csv.reader(io.StringIO(vehicles_csv))
        header = next(vehicle_reader)
        for row in vehicle_reader:
            vehicle_external_id, vin, price, release_year, mileage = row
            Vehicle.objects.update_or_create(
                external_id=vehicle_external_id,
                defaults={
                    'vin': vin,
                    'price': price,
                    'release_year': release_year,
                    'mileage': mileage,
                    'enterprise': enterprise_obj
                }
            )

        # 3) routes.csv
        #    route_external_id, vehicle_external_id, start_time, end_time, duration
        route_reader = csv.reader(io.StringIO(routes_csv))
        header = next(route_reader)
        for row in route_reader:
            route_external_id, veh_external_id, stime, etime, dur = row

            start_time = parse_datetime(stime)
            end_time = parse_datetime(etime)

            try:
                vehicle_obj = Vehicle.objects.get(external_id=veh_external_id)
            except Vehicle.DoesNotExist:
                return Response({"detail": f"No vehicle data for route: {row}"}, status=400)
            
            # dur может быть '2:30:00', optional
            # parse stime, etime isoformat
            Route.objects.update_or_create(
                external_id=route_external_id,
                defaults={
                    'vehicle_id': vehicle_obj.id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': dur if dur else None
                }
            )

        # 4) gps_points.csv
        #    route_external_id, timestamp, lon, lat
        gps_reader = csv.reader(io.StringIO(gps_csv))
        header = next(gps_reader)
        for row in gps_reader:
            route_external_id, ts, lon, lat = row
            # найдём Route
            try:
                r_obj = Route.objects.get(external_id=route_external_id)
            except Route.DoesNotExist:
                continue
            # А vehicle?
            v_obj = r_obj.vehicle
            # Cоздаём точку
            VehicleGPSPoint.objects.create(
                vehicle=v_obj,
                timestamp=ts,
                location=Point(float(lon), float(lat), srid=4326)
            )

        return Response({"detail": "CSV Import successful"}, status=200)

def parse_datetime(dt_str):
    """Функция для преобразования строки в datetime"""
    return datetime.fromisoformat(dt_str) if dt_str else None