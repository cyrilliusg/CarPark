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
    VehicleGPSPointListView, VehiclePointsByRoutesView, RouteListView,
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

]
