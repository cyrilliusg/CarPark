# urls.py
from django.urls import path, include
from .views import (
    VehicleListCreateAPIView,
    VehicleRetrieveUpdateDestroyAPIView,
    EnterpriseListCreateAPIView,
    EnterpriseRetrieveUpdateDestroyAPIView,
    DriverListCreateAPIView,
    DriverRetrieveUpdateDestroyAPIView,
    ActiveDriverAPIView,
    ActiveVehicleDriverListAPIView,
    api_login,
    login_view,
    enterprise_list_view,
    enterprise_edit_view,
    enterprise_vehicles_list_view,
    vehicle_add_view,
    vehicle_edit_view,
    vehicle_delete_view,
    VehicleGPSPointListView, VehiclePointsByRoutesView, RouteListView, vehicle_detail_view, vehicle_map_view,
    ExportEnterpriseListView, ImportEnterpriseDataJSONView, ImportEnterpriseDataCSVView, report_list_view,
    create_mileage_report_view, report_detail_view, MileageReportAPIView, upload_trip_view,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ...
    # Маршруты для Vehicle
    path('api/vehicles/', VehicleListCreateAPIView.as_view(), name='vehicle-list-create'),
    path('api/vehicles/<int:pk>/', VehicleRetrieveUpdateDestroyAPIView.as_view(), name='vehicle-detail'),

    # Маршруты для Enterprise
    path('api/enterprises/', EnterpriseListCreateAPIView.as_view(), name='enterprise-list-create'),
    path('api/enterprises/<int:pk>/', EnterpriseRetrieveUpdateDestroyAPIView.as_view(), name='enterprise-detail'),

    # Маршруты для Driver
    path('api/drivers/', DriverListCreateAPIView.as_view(), name='driver-list-create'),
    path('api/drivers/<int:pk>/', DriverRetrieveUpdateDestroyAPIView.as_view(), name='driver-detail'),

    path('api/vehicles/<int:vehicle_id>/active_driver/', ActiveDriverAPIView.as_view(), name='active-driver'),
    path('api/active-vehicles/', ActiveVehicleDriverListAPIView.as_view(), name='active-vehicles'),

    # Аутентификация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/login/', api_login, name='api-login'),

    path('login/', login_view, name='login-view'),
    path('enterprises/', enterprise_list_view, name='enterprise-list-view'),
    path('enterprises/<int:pk>/edit/', enterprise_edit_view, name='enterprise-edit'),

    path('enterprises/<int:pk>/vehicles/', enterprise_vehicles_list_view, name='enterprise-vehicles-list'),
    path('enterprises/<int:pk>/vehicles/add/', vehicle_add_view, name='vehicle-add'),
    path('enterprises/<int:pk>/vehicles/<int:vehicle_id>/edit/', vehicle_edit_view, name='vehicle-edit'),
    path('enterprises/<int:pk>/vehicles/<int:vehicle_id>/delete/', vehicle_delete_view, name='vehicle-delete'),

    path('api/gps-points/', VehicleGPSPointListView.as_view(), name='gps-points-list'),
    path('api/gps-points/<int:vehicle_id>/', VehicleGPSPointListView.as_view(), name='gps-point-list-specific'),

    path('api/routes/points/', VehiclePointsByRoutesView.as_view(), name='routes-points-list'),

    path('api/routes/', RouteListView.as_view(), name='route-list'),

    path('enterprises/<int:pk>/vehicles/<int:vehicle_id>/', vehicle_detail_view, name='vehicle-detail'),
    path('enterprises/<int:pk>/vehicles/<int:vehicle_id>/map/', vehicle_map_view, name='vehicle-map'),

    path('api/export-enterprise-data/', ExportEnterpriseListView.as_view(), name='export_enterprise_data'),

    path('api/import-enterprise-data-json/', ImportEnterpriseDataJSONView.as_view(), name='import-enterprise-json'),
    path('api/import-enterprise-data-csv/', ImportEnterpriseDataCSVView.as_view(), name='import-enterprise-csv'),

    # 1. Веб-интерфейс отчётов
    path('reports/', report_list_view, name='report-list-view'),  # Список отчётов
    path('reports/<int:pk>/', report_detail_view, name='report-detail'),  # Детальный просмотр отчёта
    path('reports/create/mileage/', create_mileage_report_view, name='create-mileage-report'),
    # Создать отчёт о пробеге

    # 2. REST API для отчётов
    path('api/reports/mileage/', MileageReportAPIView.as_view(), name='mileage-report-api'),
    # API для пробега автомобиля

    path('vehicles/upload_trip/', upload_trip_view, name='upload_trip'),

]
